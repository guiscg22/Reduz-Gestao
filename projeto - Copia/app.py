import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Define o caminho de upload de forma relativa
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Comprovantes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Demais classes e rotas...

@app.route('/financeiro', methods=['GET', 'POST'])
def financeiro():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            for cliente in Cliente.query.all():
                financeiro = Financeiro.query.filter_by(cliente_id=cliente.id).first()
                if not financeiro:
                    financeiro = Financeiro(cliente_id=cliente.id)
                    db.session.add(financeiro)

                financeiro.data_fechamento = datetime.strptime(request.form.get(f'data_fechamento_{cliente.id}'), '%Y-%m-%d').date() if request.form.get(f'data_fechamento_{cliente.id}') else None
                financeiro.numero_orcamento = request.form.get(f'numero_orcamento_{cliente.id}')
                financeiro.numero_nota_fiscal = request.form.get(f'numero_nota_fiscal_{cliente.id}')
                
                valor_fechado_str = request.form.get(f'valor_fechado_{cliente.id}')
                financeiro.valor_fechado = float(valor_fechado_str.replace('.', '').replace(',', '.')) if valor_fechado_str else 0
                
                financeiro.forma_pagamento = request.form.get(f'forma_pagamento_{cliente.id}')
                financeiro.observacao = request.form.get(f'observacao_{cliente.id}')

                # Reset valor recebido antes de calcular
                financeiro.valor_recebido = 0
                pagamentos = Pagamento.query.filter_by(financeiro_id=financeiro.id).all()

                # Remover pagamentos marcados
                removed_payments = [key.split('_')[2] for key, value in request.form.items() if key.startswith('removed_') and value == 'true']
                for pagamento in pagamentos:
                    if str(pagamento.id) in removed_payments:
                        db.session.delete(pagamento)
                    else:
                        pagamento.data_pagamento = datetime.strptime(request.form.get(f'data_pagamento_{cliente.id}_{pagamento.id}'), '%Y-%m-%d').date()
                        pagamento.forma_pagamento = request.form.get(f'forma_pagamento_{cliente.id}_{pagamento.id}')
                        
                        valor_pagamento_str = request.form.get(f'valor_pagamento_{cliente.id}_{pagamento.id}')
                        pagamento.valor = float(valor_pagamento_str.replace('.', '').replace(',', '.')) if valor_pagamento_str else 0
                        
                        financeiro.valor_recebido += pagamento.valor

                # Adicionar novos pagamentos
                num_pagamentos = int(request.form.get(f'num_pagamentos_{cliente.id}', 0))
                for i in range(1, num_pagamentos + 1):
                    data_pagamento = datetime.strptime(request.form.get(f'data_pagamento_{cliente.id}_new_{i}'), '%Y-%m-%d').date() if request.form.get(f'data_pagamento_{cliente.id}_new_{i}') else None
                    forma_pagamento = request.form.get(f'forma_pagamento_{cliente.id}_new_{i}')
                    
                    valor_pagamento_str = request.form.get(f'valor_pagamento_{cliente.id}_new_{i}')
                    valor = float(valor_pagamento_str.replace('.', '').replace(',', '.')) if valor_pagamento_str else 0
                    
                    comprovante = request.files.get(f'comprovante_{cliente.id}_new_{i}')

                    if data_pagamento and forma_pagamento and valor:
                        # Criar diretório do cliente se não existir
                        client_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(cliente.id))
                        if not os.path.exists(client_folder):
                            os.makedirs(client_folder)

                        comprovante_filename = None
                        if comprovante:
                            comprovante_filename = f'{cliente.id}_{comprovante.filename}'
                            comprovante.save(os.path.join(client_folder, comprovante_filename))

                        pagamento = Pagamento(
                            financeiro_id=financeiro.id,
                            data_pagamento=data_pagamento,
                            forma_pagamento=forma_pagamento,
                            valor=valor,
                            comprovante=comprovante_filename
                        )
                        db.session.add(pagamento)
                        financeiro.valor_recebido += valor

            db.session.commit()
            flash('Dados financeiros salvos com sucesso!', 'success')
            return redirect(url_for('financeiro'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar financeiro: {e}", 'error')
    financeiros = Financeiro.query.all()
    clientes = Cliente.query.all()

    total_valor_fechado = sum(f.valor_fechado for f in financeiros if f.valor_fechado)
    total_valor_recebido = sum(f.valor_recebido for f in financeiros if f.valor_recebido)
    diferenca = total_valor_fechado - total_valor_recebido

    return render_template('financeiro.html', financeiros=financeiros, clientes=clientes, total_valor_fechado=total_valor_fechado, total_valor_recebido=total_valor_recebido, diferenca=diferenca)

@app.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        pagamento = Pagamento.query.get(payment_id)
        if pagamento:
            db.session.delete(pagamento)
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Pagamento não encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/comprovantes/<int:cliente_id>/<filename>')
def get_comprovante(cliente_id, filename):
    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(cliente_id))
    return send_from_directory(client_folder, filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

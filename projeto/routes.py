from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, Cliente, Compra, Obra, Engenharia, Financeiro, Pagamento
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
        flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding user: {e}', 'danger')
    users = User.query.all()
    return render_template('usuarios.html', users=users)

@main.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.usuarios'))
        except Exception as e:
            flash(f'Error updating user: {e}', 'danger')
    return render_template('editar_usuario.html', user=user)

@main.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    return redirect(url_for('main.usuarios'))

@main.before_request
def before_request():
    if not User.query.filter_by(username='alisson').first():
        db.session.add(User(username='alisson', password=generate_password_hash('123456')))
    if not User.query.filter_by(username='guilherme').first():
        db.session.add(User(username='guilherme', password=generate_password_hash('123456')))
    db.session.commit()

@main.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        novo_cliente = Cliente(nome=nome, cpf=cpf, endereco=endereco)
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            return redirect('/clientes')
        except:
            flash('Erro ao adicionar cliente')
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@main.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.cpf = request.form['cpf']
        cliente.endereco = request.form['endereco']
        try:
            db.session.commit()
            return redirect('/clientes')
        except:
            flash('Erro ao editar cliente')
    return render_template('editar_cliente.html', cliente=cliente)

@main.route('/clientes/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    try:
        cliente = Cliente.query.get(id)
        if cliente:
            db.session.delete(cliente)
            db.session.commit()
            flash('Cliente excluído com sucesso!', 'success')
        else:
            flash('Cliente não encontrado.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cliente: {e}', 'error')
    finally:
        return redirect(url_for('main.listar_clientes'))

@main.route('/clientes')
def listar_clientes():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    clientes = Cliente.query.all()
    return render_template('listar_clientes.html', clientes=clientes)

@main.route('/clientes/salvar', methods=['POST'])
def salvar_cliente():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    cpf = request.form.get('cpf')

    novo_cliente = Cliente(nome=nome, endereco=endereco, cpf=cpf)
    try:
        db.session.add(novo_cliente)
        db.session.commit()
        flash('Cliente salvo com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar cliente: {e}', 'error')

    return redirect(url_for('main.listar_clientes'))

@main.route('/compras', methods=['GET', 'POST'])
def compras():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        try:
            for cliente in Cliente.query.all():
                compra = Compra.query.filter_by(cliente_id=cliente.id).first()
                if not compra:
                    compra = Compra(cliente_id=cliente.id)
                    db.session.add(compra)
                
                compra.orcamento = request.form.get(f'orcamento_{cliente.id}')
                compra.nota_fiscal = request.form.get(f'nota_fiscal_{cliente.id}')
                compra.status = request.form.get(f'status_{cliente.id}')
            db.session.commit()
            return redirect(url_for('main.compras'))
        except Exception as e:
            flash(f"Erro ao salvar compras: {e}")
    compras = Compra.query.all()
    clientes = Cliente.query.all()
    return render_template('compras.html', compras=compras, clientes=clientes)

@main.route('/obras', methods=['GET', 'POST'])
def obras():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        try:
            for cliente in Cliente.query.all():
                obra = Obra.query.filter_by(cliente_id=cliente.id).first()
                if not obra:
                    obra = Obra(cliente_id=cliente.id)
                    db.session.add(obra)
                
                obra.modulo = request.form.get(f'modulo_{cliente.id}')
                obra.inversor = request.form.get(f'inversor_{cliente.id}')
                obra.estrutura = request.form.get(f'estrutura_{cliente.id}')
                obra.pago = bool(request.form.get(f'pago_{cliente.id}'))
                obra.obra_interna_concluida = bool(request.form.get(f'obra_interna_concluida_{cliente.id}'))
                obra.data_instalacao = datetime.strptime(request.form.get(f'data_instalacao_{cliente.id}'), '%Y-%m-%d').date() if request.form.get(f'data_instalacao_{cliente.id}') else None
                obra.status = request.form.get(f'status_{cliente.id}')
            db.session.commit()
            return redirect(url_for('main.obras'))
        except Exception as e:
            flash(f"Erro ao salvar obras: {e}")
    obras = Obra.query.all()
    clientes = Cliente.query.all()
    return render_template('obras.html', obras=obras, clientes=clientes)

@main.route('/engenharia', methods=['GET', 'POST'])
def engenharia():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        try:
            for cliente in Cliente.query.all():
                engenharia = Engenharia.query.filter_by(cliente_id=cliente.id).first()
                if not engenharia:
                    engenharia = Engenharia(cliente_id=cliente.id)
                    db.session.add(engenharia)
                
                engenharia.documentos_comercial = 'documentos_comercial_' + str(cliente.id) in request.form
                engenharia.analise_documentos = 'analise_documentos_' + str(cliente.id) in request.form
                engenharia.formulario_acesso_comercial = 'formulario_acesso_comercial_' + str(cliente.id) in request.form
                engenharia.procuracao_assinada = 'procuracao_assinada_' + str(cliente.id) in request.form
                engenharia.emissao_pagamento_art = 'emissao_pagamento_art_' + str(cliente.id) in request.form
                engenharia.enviado_cemig = 'enviado_cemig_' + str(cliente.id) in request.form
                engenharia.projeto_aprovado = 'projeto_aprovado_' + str(cliente.id) in request.form
                engenharia.obra_cemig_concluida = 'obra_cemig_concluida_' + str(cliente.id) in request.form
                engenharia.obra_interna_concluida = 'obra_interna_concluida_' + str(cliente.id) in request.form
                engenharia.vistoria_solicitada = 'vistoria_solicitada_' + str(cliente.id) in request.form
                engenharia.vistoria_aprovada = 'vistoria_aprovada_' + str(cliente.id) in request.form
                engenharia.observacao = request.form.get(f'observacao_{cliente.id}')
                engenharia.status = request.form.get(f'status_{cliente.id}')
                engenharia.data_limite_parecer = datetime.strptime(request.form.get(f'data_limite_parecer_{cliente.id}'), '%Y-%m-%d').date() if request.form.get(f'data_limite_parecer_{cliente.id}') else None
            db.session.commit()
            return redirect(url_for('main.engenharia'))
        except Exception as e:
            flash(f"Erro ao salvar engenharia: {e}")
    engenharias = Engenharia.query.all()
    clientes = Cliente.query.all()
    return render_template('engenharia.html', engenharias=engenharias, clientes=clientes)

@main.route('/financeiro', methods=['GET', 'POST'])
def financeiro():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
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

                financeiro.valor_recebido = 0
                pagamentos = Pagamento.query.filter_by(financeiro_id=financeiro.id).all()

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

                num_pagamentos = int(request.form.get(f'num_pagamentos_{cliente.id}', 0))
                for i in range(1, num_pagamentos + 1):
                    data_pagamento = datetime.strptime(request.form.get(f'data_pagamento_{cliente.id}_new_{i}'), '%Y-%m-%d').date() if request.form.get(f'data_pagamento_{cliente.id}_new_{i}') else None
                    forma_pagamento = request.form.get(f'forma_pagamento_{cliente.id}_new_{i}')
                    
                    valor_pagamento_str = request.form.get(f'valor_pagamento_{cliente.id}_new_{i}')
                    valor = float(valor_pagamento_str.replace('.', '').replace(',', '.')) if valor_pagamento_str else 0
                    
                    comprovante = request.files.get(f'comprovante_{cliente.id}_new_{i}')

                    if data_pagamento and forma_pagamento and valor:
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
            return redirect(url_for('main.financeiro'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar financeiro: {e}", 'error')
    financeiros = Financeiro.query.all()
    clientes = Cliente.query.all()

    total_valor_fechado = sum(f.valor_fechado for f in financeiros if f.valor_fechado)
    total_valor_recebido = sum(f.valor_recebido for f in financeiros if f.valor_recebido)
    diferenca = total_valor_fechado - total_valor_recebido

    return render_template('financeiro.html', financeiros=financeiros, clientes=clientes, total_valor_fechado=total_valor_fechado, total_valor_recebido=total_valor_recebido, diferenca=diferenca)

@main.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
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

@main.route('/comprovantes/<int:cliente_id>/<filename>')
def get_comprovante(cliente_id, filename):
    client_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(cliente_id))
    return send_from_directory(client_folder, filename)

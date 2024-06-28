import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure the database connection
database_url = os.getenv('DATABASE_URL', 'postgresql://reduzgestao_user:hAvAVESGXiKKUJfMjddrPWYoOo5oxftE@dpg-cpsvf0mehbks73eroe40-a.oregon-postgres.render.com/reduzgestao')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'Comprovantes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # Adjusted for CPF format
    endereco = db.Column(db.String(200), nullable=False)
    compras = db.relationship('Compra', backref='cliente', cascade="all, delete-orphan", lazy=True)
    obras = db.relationship('Obra', backref='cliente', cascade="all, delete-orphan", lazy=True)
    engenharias = db.relationship('Engenharia', backref='cliente', cascade="all, delete-orphan", lazy=True)
    financeiros = db.relationship('Financeiro', backref='cliente', cascade="all, delete-orphan", lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    orcamento = db.Column(db.String(100), nullable=True)
    nota_fiscal = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=True)

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    modulo = db.Column(db.String(100), nullable=True)
    inversor = db.Column(db.String(100), nullable=True)
    estrutura = db.Column(db.String(100), nullable=True)
    pago = db.Column(db.Boolean, nullable=False, default=False)
    obra_interna_concluida = db.Column(db.Boolean, nullable=False, default=False)
    data_instalacao = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=True)

class Engenharia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    documentos_comercial = db.Column(db.Boolean, nullable=False, default=False)
    analise_documentos = db.Column(db.Boolean, nullable=False, default=False)
    formulario_acesso_comercial = db.Column(db.Boolean, nullable=False, default=False)
    procuracao_assinada = db.Column(db.Boolean, nullable=False, default=False)
    emissao_pagamento_art = db.Column(db.Boolean, nullable=False, default=False)
    enviado_cemig = db.Column(db.Boolean, nullable=False, default=False)
    projeto_aprovado = db.Column(db.Boolean, nullable=False, default=False)
    obra_cemig_concluida = db.Column(db.Boolean, nullable=False, default=False)
    obra_interna_concluida = db.Column(db.Boolean, nullable=False, default=False)
    vistoria_solicitada = db.Column(db.Boolean, nullable=False, default=False)
    vistoria_aprovada = db.Column(db.Boolean, nullable=False, default=False)
    observacao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    data_limite_parecer = db.Column(db.Date, nullable=True)

class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    data_fechamento = db.Column(db.Date, nullable=True)
    numero_orcamento = db.Column(db.String(100), nullable=True)
    numero_nota_fiscal = db.Column(db.String(100), nullable=True)
    valor_fechado = db.Column(db.Float, nullable=True)
    forma_pagamento = db.Column(db.String(50), nullable=True)
    valor_recebido = db.Column(db.Float, nullable=True, default=0.0)
    observacao = db.Column(db.Text, nullable=True)
    pagamentos = db.relationship('Pagamento', backref='financeiro', cascade="all, delete-orphan", lazy=True)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    financeiro_id = db.Column(db.Integer, db.ForeignKey('financeiro.id', ondelete='CASCADE'), nullable=False)
    data_pagamento = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    comprovante = db.Column(db.String(200), nullable=True)

@app.before_first_request
def test_connection():
    try:
        db.session.execute('SELECT 1')
        app.logger.info("Conexão ao banco de dados bem-sucedida.")
    except Exception as e:
        app.logger.error(f"Erro ao conectar ao banco de dados: {e}")
    

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(username=username, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding user: {e}', 'danger')
    users = User.query.all()
    return render_template('usuarios.html', users=users)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='sha256')
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('usuarios'))
        except Exception as e:
            flash(f'Error updating user: {e}', 'danger')
    return render_template('editar_usuario.html', user=user)

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    return redirect(url_for('usuarios'))

@app.before_request
def before_request():
    if not User.query.filter_by(username='alisson').first():
        db.session.add(User(username='alisson', password=generate_password_hash('123456', method='sha256')))
    if not User.query.filter_by(username='guilherme').first():
        db.session.add(User(username='guilherme', password=generate_password_hash('123456', method='sha256')))
    db.session.commit()

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

@app.route('/clientes/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
        return redirect(url_for('listar_clientes'))

@app.route('/clientes')
def listar_clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    clientes = Cliente.query.all()
    return render_template('listar_clientes.html', clientes=clientes)

@app.route('/clientes/salvar', methods=['POST'])
def salvar_cliente():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

    return redirect(url_for('listar_clientes'))

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            for cliente in Cliente.query.all():
                compra = Compra.query.filter_by(cliente_id=cliente.id).first()
                if not compra:
                    compra = Compra(cliente_id=cliente.id)
                    db.session.add(compra)
                
                app.logger.info(f"Processando cliente ID: {cliente.id}")
                
                data_compra = request.form.get(f'data_compra_{cliente.id}')
                produto = request.form.get(f'produto_{cliente.id}')
                quantidade = request.form.get(f'quantidade_{cliente.id}')
                valor_total = request.form.get(f'valor_total_{cliente.id}')
                status_entrega = request.form.get(f'status_entrega_{cliente.id}')
                
                app.logger.info(f"Data da Compra: {data_compra}, Produto: {produto}, Quantidade: {quantidade}, Valor Total: {valor_total}, Status da Entrega: {status_entrega}")
                
                compra.data_compra = datetime.strptime(data_compra, '%Y-%m-%d').date() if data_compra else None
                compra.produto = produto
                compra.quantidade = int(quantidade) if quantidade else 0
                compra.valor_total = float(valor_total.replace(',', '.')) if valor_total else 0.0
                compra.status_entrega = status_entrega
                
            db.session.commit()
            flash('Compras salvas com sucesso!', 'success')
            return redirect(url_for('compras'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao salvar compras: {e}")
            flash(f"Erro ao salvar compras: {e}", 'danger')
    clientes = Cliente.query.all()
    return render_template('compras.html', clientes=clientes)





@app.route('/obras', methods=['GET', 'POST'])
def obras():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
            return redirect(url_for('obras'))
        except Exception as e:
            flash(f"Erro ao salvar obras: {e}")
    obras = Obra.query.all()
    clientes = Cliente.query.all()
    return render_template('obras.html', obras=obras, clientes=clientes)

@app.route('/engenharia', methods=['GET', 'POST'])
def engenharia():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
            return redirect(url_for('engenharia'))
        except Exception as e:
            flash(f"Erro ao salvar engenharia: {e}")
    engenharias = Engenharia.query.all()
    clientes = Cliente.query.all()
    return render_template('engenharia.html', engenharias=engenharias, clientes=clientes)

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

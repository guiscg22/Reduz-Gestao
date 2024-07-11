import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'C:/Users/Guilherme/Desktop/project - Copia - Copia - Copia/Comprovantes'
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
    modulo = db.Column(db.String(100), nullable=True)
    inversor = db.Column(db.String(100), nullable=True)
    estrutura = db.Column(db.String(100), nullable=True)
    valor_total = db.Column(db.Float, nullable=True)
    status_entrega = db.Column(db.String(20), nullable=True)
    data_compra = db.Column(db.Date, nullable=True)

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
            flash('Erro ao atualizar cliente')
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/clientes/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        return redirect('/clientes')
    except:
        flash('Erro ao excluir cliente')

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

                data_compra = request.form.get(f'data_compra_{cliente.id}')
                if data_compra:
                    compra.data_compra = datetime.strptime(data_compra, '%Y-%m-%d').date()
                else:
                    compra.data_compra = None

                compra.orcamento = request.form.get(f'orcamento_{cliente.id}') or ''
                compra.modulo = request.form.get(f'modulo_{cliente.id}') or ''
                compra.inversor = request.form.get(f'inversor_{cliente.id}') or ''
                compra.estrutura = request.form.get(f'estrutura_{cliente.id}') or ''

                valor_total_str = request.form.get(f'valor_total_{cliente.id}')
                compra.valor_total = float(valor_total_str.replace('.', '').replace(',', '.')) if valor_total_str else None

                compra.status_entrega = request.form.get(f'status_entrega_{cliente.id}') or ''
            db.session.commit()
            flash('Compras salvas com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar compras: {e}", 'danger')

    clientes = Cliente.query.all()
    for cliente in clientes:
        cliente.compras = Compra.query.filter_by(cliente_id=cliente.id).all()
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

                obra.modulo = request.form.get(f'modulo_{cliente.id}') or ''
                obra.inversor = request.form.get(f'inversor_{cliente.id}') or ''
                obra.estrutura = request.form.get(f'estrutura_{cliente.id}') or ''
                obra.pago = 'pago' in request.form.getlist(f'pago_{cliente.id}')
                obra.obra_interna_concluida = 'obra_interna_concluida' in request.form.getlist(f'obra_interna_concluida_{cliente.id}')
                obra.status = request.form.get(f'status_{cliente.id}') or ''

                data_instalacao = request.form.get(f'data_instalacao_{cliente.id}')
                if data_instalacao:
                    obra.data_instalacao = datetime.strptime(data_instalacao, '%Y-%m-%d').date()
                else:
                    obra.data_instalacao = None

            db.session.commit()
            flash('Obras salvas com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar obras: {e}", 'danger')

    clientes = Cliente.query.all()
    for cliente in clientes:
        cliente.obras = Obra.query.filter_by(cliente_id=cliente.id).all()
    return render_template('obras.html', clientes=clientes)

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

                engenharia.documentos_comercial = 'documentos_comercial' in request.form.getlist(f'documentos_comercial_{cliente.id}')
                engenharia.analise_documentos = 'analise_documentos' in request.form.getlist(f'analise_documentos_{cliente.id}')
                engenharia.formulario_acesso_comercial = 'formulario_acesso_comercial' in request.form.getlist(f'formulario_acesso_comercial_{cliente.id}')
                engenharia.procuracao_assinada = 'procuracao_assinada' in request.form.getlist(f'procuracao_assinada_{cliente.id}')
                engenharia.emissao_pagamento_art = 'emissao_pagamento_art' in request.form.getlist(f'emissao_pagamento_art_{cliente.id}')
                engenharia.enviado_cemig = 'enviado_cemig' in request.form.getlist(f'enviado_cemig_{cliente.id}')
                engenharia.projeto_aprovado = 'projeto_aprovado' in request.form.getlist(f'projeto_aprovado_{cliente.id}')
                engenharia.obra_cemig_concluida = 'obra_cemig_concluida' in request.form.getlist(f'obra_cemig_concluida_{cliente.id}')
                engenharia.obra_interna_concluida = 'obra_interna_concluida' in request.form.getlist(f'obra_interna_concluida_{cliente.id}')
                engenharia.vistoria_solicitada = 'vistoria_solicitada' in request.form.getlist(f'vistoria_solicitada_{cliente.id}')
                engenharia.vistoria_aprovada = 'vistoria_aprovada' in request.form.getlist(f'vistoria_aprovada_{cliente.id}')
                engenharia.observacao = request.form.get(f'observacao_{cliente.id}') or ''
                engenharia.status = request.form.get(f'status_{cliente.id}') or ''

                data_limite_parecer = request.form.get(f'data_limite_parecer_{cliente.id}')
                if data_limite_parecer:
                    engenharia.data_limite_parecer = datetime.strptime(data_limite_parecer, '%Y-%m-%d').date()
                else:
                    engenharia.data_limite_parecer = None

            db.session.commit()
            flash('Engenharia salva com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar engenharia: {e}", 'danger')

    clientes = Cliente.query.all()
    for cliente in clientes:
        cliente.engenharias = Engenharia.query.filter_by(cliente_id=cliente.id).all()
    return render_template('engenharia.html', clientes=clientes)

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

                data_fechamento = request.form.get(f'data_fechamento_{cliente.id}')
                if data_fechamento:
                    financeiro.data_fechamento = datetime.strptime(data_fechamento, '%Y-%m-%d').date()
                else:
                    financeiro.data_fechamento = None

                financeiro.numero_orcamento = request.form.get(f'numero_orcamento_{cliente.id}') or ''
                financeiro.numero_nota_fiscal = request.form.get(f'numero_nota_fiscal_{cliente.id}') or ''

                valor_fechado_str = request.form.get(f'valor_fechado_{cliente.id}')
                financeiro.valor_fechado = float(valor_fechado_str.replace('.', '').replace(',', '.')) if valor_fechado_str else None

                valor_recebido_str = request.form.get(f'valor_recebido_{cliente.id}')
                financeiro.valor_recebido = float(valor_recebido_str.replace('.', '').replace(',', '.')) if valor_recebido_str else None

                financeiro.observacao = request.form.get(f'observacao_{cliente.id}') or ''

            db.session.commit()
            flash('Dados financeiros salvos com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar dados financeiros: {e}", 'danger')

    clientes = Cliente.query.all()
    for cliente in clientes:
        cliente.financeiros = Financeiro.query.filter_by(cliente_id=cliente.id).all()
    return render_template('financeiro.html', clientes=clientes)

if __name__ == '__main__':
    app.run(debug=True)

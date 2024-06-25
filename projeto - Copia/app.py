from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(300))

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    orcamento = db.Column(db.String(100))
    nota_fiscal = db.Column(db.String(100))
    status = db.Column(db.String(100))

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    modulo = db.Column(db.String(100))
    inversor = db.Column(db.String(100))
    estrutura = db.Column(db.String(100))
    pago = db.Column(db.Boolean, default=False)
    obra_interna_concluida = db.Column(db.Boolean, default=False)
    data_instalacao = db.Column(db.Date)
    status = db.Column(db.String(100))

class Engenharia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    documentos_comercial = db.Column(db.Boolean, default=False)
    analise_documentos = db.Column(db.Boolean, default=False)
    formulario_acesso_comercial = db.Column(db.Boolean, default=False)
    procuracao_assinada = db.Column(db.Boolean, default=False)
    emissao_pagamento_art = db.Column(db.Boolean, default=False)
    enviado_cemig = db.Column(db.Boolean, default=False)
    projeto_aprovado = db.Column(db.Boolean, default=False)
    obra_cemig_concluida = db.Column(db.Boolean, default=False)
    obra_interna_concluida = db.Column(db.Boolean, default=False)
    vistoria_solicitada = db.Column(db.Boolean, default=False)
    vistoria_aprovada = db.Column(db.Boolean, default=False)
    observacao = db.Column(db.String(300))
    status = db.Column(db.String(100))
    data_limite_parecer = db.Column(db.Date)

class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data_fechamento = db.Column(db.Date)
    numero_orcamento = db.Column(db.String(100))
    numero_nota_fiscal = db.Column(db.String(100))
    valor_fechado = db.Column(db.Float)
    forma_pagamento = db.Column(db.String(100))
    valor_recebido = db.Column(db.Float)
    observacao = db.Column(db.String(300))
    pagamentos = db.relationship('Pagamento', backref='financeiro', lazy=True)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    financeiro_id = db.Column(db.Integer, db.ForeignKey('financeiro.id'), nullable=False)
    data_pagamento = db.Column(db.Date)
    forma_pagamento = db.Column(db.String(100))
    valor = db.Column(db.Float)
    comprovante = db.Column(db.String(300))

# Rotas e lógica
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
            return redirect(url_for('index'))
        else:
            flash('Login inválido. Tente novamente.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

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
            flash('Cliente adicionado com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro ao adicionar cliente', 'error')
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

@app.route('/clientes/excluir/<int:id>', methods=['POST'])
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
        return redirect(url_for('clientes'))

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
                
                compra.orcamento = request.form.get(f'orcamento_{cliente.id}')
                compra.nota_fiscal = request.form.get(f'nota_fiscal_{cliente.id}')
                compra.status = request.form.get(f'status_{cliente.id}')
            db.session.commit()
            return redirect(url_for('compras'))
        except Exception as e:
            flash(f"Erro ao salvar compras: {e}")
    compras = Compra.query.all()
    clientes = Cliente.query.all()
    return render_template('compras.html', compras=compras, clientes=clientes)

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
                
                engenharia.documentos_comercial = bool(request.form.get(f'documentos_comercial_{cliente.id}'))
                engenharia.analise_documentos = bool(request.form.get(f'analise_documentos_{cliente.id}'))
                engenharia.formulario_acesso_comercial = bool(request.form.get(f'formulario_acesso_comercial_{cliente.id}'))
                engenharia.procuracao_assinada = bool(request.form.get(f'procuracao_assinada_{cliente.id}'))
                engenharia.emissao_pagamento_art = bool(request.form.get(f'emissao_pagamento_art_{cliente.id}'))
                engenharia.enviado_cemig = bool(request.form.get(f'enviado_cemig_{cliente.id}'))
                engenharia.projeto_aprovado = bool(request.form.get(f'projeto_aprovado_{cliente.id}'))
                engenharia.obra_cemig_concluida = bool(request.form.get(f'obra_cemig_concluida_{cliente.id}'))
                engenharia.obra_interna_concluida = bool(request.form.get(f'obra_interna_concluida_{cliente.id}'))
                engenharia.vistoria_solicitada = bool(request.form.get(f'vistoria_solicitada_{cliente.id}'))
                engenharia.vistoria_aprovada = bool(request.form.get(f'vistoria_aprovada_{cliente.id}'))
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
                financeiro.valor_fechado = float(request.form.get(f'valor_fechado_{cliente.id}')) if request.form.get(f'valor_fechado_{cliente.id}') else 0.0
                financeiro.forma_pagamento = request.form.get(f'forma_pagamento_{cliente.id}')
                financeiro.valor_recebido = float(request.form.get(f'valor_recebido_{cliente.id}')) if request.form.get(f'valor_recebido_{cliente.id}') else 0.0
                financeiro.observacao = request.form.get(f'observacao_{cliente.id}')
            db.session.commit()
            return redirect(url_for('financeiro'))
        except Exception as e:
            flash(f"Erro ao salvar financeiro: {e}")
    financeiros = Financeiro.query.all()
    clientes = Cliente.query.all()
    return render_template('financeiro.html', financeiros=financeiros, clientes=clientes)

if __name__ == "__main__":
    app.run(debug=True)

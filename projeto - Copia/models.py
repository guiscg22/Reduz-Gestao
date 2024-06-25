from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
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

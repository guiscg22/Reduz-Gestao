class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    endereco = db.Column(db.String(200))
    compras = db.relationship('Compra', back_populates='cliente')
    obras = db.relationship('Obra', back_populates='cliente')
    engenharias = db.relationship('Engenharia', back_populates='cliente')
    financeiros = db.relationship('Financeiro', back_populates='cliente')

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data_compra = db.Column(db.Date)
    produto = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)
    valor_total = db.Column(db.Float)
    status_entrega = db.Column(db.String(50))

    cliente = db.relationship('Cliente', back_populates='compras')

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    modulo = db.Column(db.String(100))
    inversor = db.Column(db.String(100))
    estrutura = db.Column(db.String(100))
    pago = db.Column(db.Boolean)
    trabalho_interno_concluido = db.Column(db.Boolean)
    data_instalacao = db.Column(db.Date)
    status = db.Column(db.String(50))

    cliente = db.relationship('Cliente', back_populates='obras')

class Engenharia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    documentos_comerciais = db.Column(db.String(100))
    analise_documentos = db.Column(db.String(100))
    formulario_acesso_comercial = db.Column(db.String(100))
    procuração_assinada = db.Column(db.String(100))
    emissao_pagamento_art = db.Column(db.String(100))
    enviado_para_cemig = db.Column(db.String(100))
    projeto_aprovado = db.Column(db.String(100))
    trabalho_interno_concluido = db.Column(db.String(100))
    inspeção_solicitada = db.Column(db.String(100))
    inspeção_aprovada = db.Column(db.String(100))
    observacao = db.Column(db.Text)
    status = db.Column(db.String(50))
    data_limite = db.Column(db.Date)

    cliente = db.relationship('Cliente', back_populates='engenharias')

class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data_fechamento = db.Column(db.Date)
    numero_orcamento = db.Column(db.String(100))
    numero_nota_fiscal = db.Column(db.String(100))
    valor_fechado = db.Column(db.Float)
    metodo_pagamento = db.Column(db.String(50))
    valor_recebido = db.Column(db.Float)
    observacao = db.Column(db.Text)

    cliente = db.relationship('Cliente', back_populates='financeiros')

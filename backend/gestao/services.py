import hashlib
from io import BytesIO
from textwrap import wrap
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def gerar_pdf_termo(reserva):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _, altura = A4
    y = altura - 3 * cm

    c.setFont('Helvetica-Bold', 16)
    c.drawString(2 * cm, y, 'TERMO DE ISENÇÃO DE RESPONSABILIDADE')
    y -= 1.5 * cm

    c.setFont('Helvetica', 11)
    usuario = reserva.usuario
    linhas = [
        f'Organizador responsável: {usuario.get_full_name() or usuario.username}',
        f'CPF: {usuario.cpf}',
        f'Data de nascimento: {usuario.data_nascimento.strftime("%d/%m/%Y")}',
        '',
        f'Arena reservada: {reserva.arena.nome}',
        f'Data/hora: {reserva.data_hora_inicio.strftime("%d/%m/%Y %H:%M")} até '
        f'{reserva.data_hora_fim.strftime("%d/%m/%Y %H:%M")}',
        '',
        'Participantes declarados:',
    ]
    for linha in linhas:
        c.drawString(2 * cm, y, linha)
        y -= 0.7 * cm

    participantes = reserva.participantes.all()
    if participantes:
        for p in participantes:
            c.drawString(2.5 * cm, y, f'- {p.nome_completo}')
            y -= 0.6 * cm
    else:
        c.drawString(2.5 * cm, y, '(nenhum participante adicional cadastrado)')
        y -= 0.6 * cm

    y -= 0.5 * cm
    texto_termo = (
        'Ao assinar este termo, o organizador acima identificado declara estar ciente dos '
        'riscos inerentes à prática de airsoft/paintball, assume responsabilidade pela '
        'orientação de segurança de todos os participantes listados, e isenta o campo '
        'SGC-Tático de responsabilidade por lesões decorrentes do uso inadequado de '
        'equipamentos ou desrespeito às normas de segurança informadas no local.'
    )
    for linha in wrap(texto_termo, 95):
        c.drawString(2 * cm, y, linha)
        y -= 0.6 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def gerar_hash_assinatura(reserva, ip):
    conteudo = f'{reserva.id}-{reserva.usuario.cpf}-{reserva.criado_em.isoformat()}-{ip}'
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()
#!/usr/bin/env python3

"""
Configuração central do gateway de alertas da Defesa Civil.

Este é o principal arquivo que uma nova instalação precisa editar.
O código do projeto não deve precisar ser alterado para configurar
outro local ou outra instalação.
"""

# ============================================================
# IDENTIFICAÇÃO DA INSTALAÇÃO
# ============================================================

# Nome usado para identificar localmente esta instalação.
#
# Pode ser uma cidade, propriedade, acampamento, veículo,
# indicativo de rádio ou qualquer outro rótulo útil.
#
# Exemplos:
#   "Ituverava"
#   "Gateway Defesa Civil - Ituverava"
#   "PU2OMT"
#   "Acampamento"
#
# Este nome NÃO é enviado automaticamente pela rede.
GATEWAY_NAME = "Gateway Defesa Civil - Campos do Jordão"


# ============================================================
# LOCALIZAÇÃO
# ============================================================

# Escolha como o gateway obterá sua posição.
#
# "manual"
#     Usa LATITUDE e LONGITUDE configuradas abaixo.
#     É o modo recomendado para uma instalação fixa.
#
# "gps"
#     Obtém a posição do GPS do nó Meshtastic.
#     A integração GPS será habilitada quando a interface
#     Meshtastic do hardware estiver integrada ao projeto.
#
LOCATION_MODE = "manual"

# Latitude utilizada no modo manual.
#
# Sul do Equador = valor negativo.
# Norte do Equador = valor positivo.
#
# Exemplo: Ituverava = -20.339
LATITUDE = -22.739

# Longitude utilizada no modo manual.
#
# Oeste de Greenwich = valor negativo.
# Leste de Greenwich = valor positivo.
#
# Exemplo: Ituverava = -47.780
LONGITUDE = -45.591


# ============================================================
# FONTE DOS ALERTAS
# ============================================================

# Feed oficial de alertas da Defesa Civil no padrão CAP.
#
# Normalmente NÃO é necessário alterar este valor.
DEFESA_CIVIL_URL = "https://idapfile.mdr.gov.br/idap/api/rss/cap"


# ============================================================
# ESTADO LOCAL
# ============================================================

# Arquivo utilizado para registrar alertas já processados.
#
# O arquivo é criado automaticamente pelo gateway.
# Ele é LOCAL e não deve ser publicado no GitHub.
STATE_FILE = "defesa_civil_state.json"


# ============================================================
# MONITORAMENTO
# ============================================================

# Intervalo entre consultas ao feed oficial da Defesa Civil,
# em segundos.
#
# 300 segundos = 5 minutos.
#
# Cada instalação pode ajustar este valor conforme sua
# necessidade. A consulta não implica transmissão:
# o gateway só transmite quando encontra um evento válido.
CHECK_INTERVAL = 300


# ============================================================
# CONTEÚDO DAS MENSAGENS
# ============================================================

# Define quais campos de texto do alerta CAP serão enviados
# pela rede Meshtastic.
#
# "default"
#     Modo recomendado para a maioria das instalações.
#
#     O gateway tenta primeiro o HEADLINE.
#     Se o HEADLINE estiver vazio, tenta a DESCRIPTION.
#     Se os dois estiverem vazios, o alerta NÃO será enviado.
#
#     A INSTRUCTION não é utilizada automaticamente no modo
#     default, pois pode conter informações complementares
#     e ser muito extensa.
#
# Você também pode escolher manualmente um ou mais campos.
#
# Exemplos:
#
#     ["headline"]
#         Envia somente o Headline.
#
#     ["description"]
#         Envia somente a Descrição.
#
#     ["instruction"]
#         Envia somente a Instrução.
#
#     ["headline", "instruction"]
#         Envia o Headline e a Instrução.
#
#     ["headline", "description", "instruction"]
#         Envia todos os campos disponíveis.
#
# Campos vazios são ignorados automaticamente.
#
# Se nenhum dos campos escolhidos tiver conteúdo,
# nenhuma mensagem será transmitida.
#
# Para uma instalação simples e econômica, deixe:
#     MESSAGE_FIELDS = "default"
MESSAGE_FIELDS = "default"


# ============================================================
# MENSAGENS MESHTASTIC
# ============================================================

# Número máximo de caracteres por mensagem.
#
# O marcador "[DEFESA CIVIL X/N]" também ocupa espaço.
# O gateway divide automaticamente uma nota oficial maior
# em várias mensagens sem cortar o conteúdo.
MAX_MESSAGE_LENGTH = 180

# Defesa Civil Meshtastic Gateway

[![CI](https://github.com/marcelositr/defesa-civil-meshtastic-gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/marcelositr/defesa-civil-meshtastic-gateway/actions/workflows/ci.yml)

Gateway de alertas oficiais da Defesa Civil para redes Meshtastic.

O projeto consulta o feed oficial de alertas no padrão **CAP (Common Alerting Protocol)**, verifica se a localização configurada está dentro da área geográfica do alerta e prepara o conteúdo oficial para retransmissão pela rede Meshtastic.

O objetivo é manter a rede silenciosa durante condições normais e transmitir somente alertas oficiais que realmente atingem a área monitorada.

## Objetivos

* Consultar automaticamente o feed oficial da Defesa Civil.
* Interpretar alertas no padrão CAP 1.2.
* Verificar a área afetada utilizando os polígonos fornecidos pelo alerta.
* Comparar os polígonos com a localização do gateway.
* Evitar retransmissões duplicadas.
* Detectar atualizações e cancelamentos de alertas.
* Ignorar alertas expirados.
* Preservar o texto oficial da Defesa Civil, sem resumo ou reescrita.
* Permitir que o operador escolha quais campos oficiais serão retransmitidos.
* Dividir mensagens longas em múltiplas mensagens compatíveis com a rede Meshtastic.
* Manter o tráfego da rede reduzido, evitando mensagens periódicas sem necessidade.

## Arquitetura

```text
Feed oficial da Defesa Civil
            |
            v
      Feed CAP / XML
            |
            v
      Parse do alerta
            |
            v
   Status / tipo CAP
            |
            v
     Área geográfica
            |
            v
      Point-in-Polygon
            |
            v
       Localização
            |
            v
     Estado / Deduplicação
            |
            v
   Seleção do conteúdo
            |
            v
     Mensagem oficial
            |
            v
       Meshtastic
```

## Fonte dos alertas

O projeto utiliza o feed oficial de alertas da Defesa Civil disponibilizado pelo Ministério da Integração e do Desenvolvimento Regional:

```text
https://idapfile.mdr.gov.br/idap/api/rss/cap
```

O conteúdo é processado no padrão **CAP 1.2**.

A aplicação não depende do nome do município presente em `areaDesc` para determinar se um alerta atinge a localização.

A área geográfica é determinada pelos polígonos fornecidos no próprio alerta CAP.

## Configuração

A configuração central fica em:

```text
config.py
```

O arquivo foi organizado para que uma nova instalação possa ser configurada sem precisar alterar o código principal.

### Identificação

```python
GATEWAY_NAME = "Gateway Defesa Civil - Campos do Jordão"
```

O nome serve para identificar localmente a instalação. Ele não é publicado automaticamente nas mensagens.

### Localização

O modo atualmente utilizado para uma instalação fixa é:

```python
LOCATION_MODE = "manual"

LATITUDE = -22.739
LONGITUDE = -45.591
```

As coordenadas são usadas localmente para verificar se o gateway está dentro da área geográfica do alerta.

Também existe a opção prevista:

```python
LOCATION_MODE = "gps"
```

A integração com o GPS do nó Meshtastic ainda será implementada.

### Intervalo de consulta

O intervalo entre consultas ao feed é configurado em segundos:

```python
CHECK_INTERVAL = 300
```

O valor pode ser ajustado conforme a necessidade da instalação.

Uma consulta ao feed não significa uma transmissão pela rede. O gateway somente prepara uma mensagem quando encontra um evento válido que afeta a localização configurada.

## Filtragem geográfica

Cada alerta pode conter um ou mais polígonos.

O gateway utiliza as coordenadas configuradas para verificar se o ponto está dentro de pelo menos um desses polígonos.

Isso permite que o projeto trabalhe com a área geográfica efetivamente fornecida pelo alerta CAP, em vez de depender apenas do nome do município.

## Processamento CAP

O projeto considera principalmente os tipos de mensagem CAP:

* `Alert`
* `Update`
* `Cancel`

Somente alertas com:

```text
status = Actual
```

são processados.

Alertas expirados não são retransmitidos.

Atualizações são relacionadas aos alertas anteriores por meio das referências CAP.

Cancelamentos tornam o alerta referenciado inativo no estado local.

## Conteúdo das mensagens

O gateway **não resume, interpreta ou reescreve** o conteúdo oficial da Defesa Civil.

A escolha dos campos retransmitidos é feita pela configuração `MESSAGE_FIELDS`.

### Modo padrão

Por padrão:

```python
MESSAGE_FIELDS = "default"
```

O gateway segue esta ordem:

1. tenta utilizar o `headline`;
2. se o `headline` estiver vazio, utiliza o `description`;
3. se ambos estiverem vazios, não transmite o alerta.

O campo `instruction` não é incluído automaticamente no modo padrão.

Essa regra existe porque o conteúdo dos alertas varia conforme a região e a situação. O projeto não tenta adivinhar qual campo é mais importante.

### Seleção manual

O operador pode escolher explicitamente quais campos deseja retransmitir:

```python
MESSAGE_FIELDS = ["headline"]
```

ou:

```python
MESSAGE_FIELDS = ["description"]
```

ou:

```python
MESSAGE_FIELDS = ["instruction"]
```

Também é possível combinar campos:

```python
MESSAGE_FIELDS = ["headline", "instruction"]
```

ou:

```python
MESSAGE_FIELDS = ["headline", "description", "instruction"]
```

Quando vários campos são selecionados, eles são enviados na mesma mensagem, separados por uma linha em branco.

Campos vazios são ignorados automaticamente. Se todos os campos selecionados estiverem vazios, nenhuma mensagem será transmitida.

O gateway não aplica filtros editoriais próprios sobre o texto. Não são feitos:

* resumo automático;
* interpretação;
* classificação própria;
* alteração de significado;
* truncamento do conteúdo oficial;
* inclusão de informações inventadas pelo gateway.

A única alteração prevista é a estrutura necessária para transportar uma mensagem longa pela rede.

## Deduplicação e estado local

O gateway mantém um estado local em:

```text
defesa_civil_state.json
```

Esse arquivo registra informações necessárias para impedir retransmissões repetidas e acompanhar o ciclo de vida dos alertas.

A identificação não depende somente do `identifier`.

Uma assinatura SHA-256 também é criada utilizando campos relevantes do alerta para permitir a detecção de alterações no mesmo alerta.

O arquivo de estado é local para cada instalação e não deve ser versionado no Git:

```gitignore
defesa_civil_state.json
```

### Limpeza automática do estado

O arquivo de estado não cresce indefinidamente.

A retenção é configurada em:

```python
STATE_RETENTION_DAYS = 30
```

O padrão de **30 dias** é deliberadamente conservador.

Registros de alertas que já expiraram ou foram cancelados podem ser removidos depois desse período. Alertas que ainda precisam permanecer no estado não são removidos simplesmente por serem antigos.

Como regra de segurança, o `config.py` recomenda manter pelo menos **3 dias** de retenção. Valores menores podem ser usados pelo operador, mas ficam sob responsabilidade da instalação.

## Fragmentação para Meshtastic

Mensagens maiores que o limite configurado são divididas em partes.

O limite padrão é:

```python
MAX_MESSAGE_LENGTH = 180
```

Cada parte recebe um marcador de transporte:

```text
[DEFESA CIVIL 1/N]
[DEFESA CIVIL 2/N]
...
```

Exemplo:

```text
[DEFESA CIVIL 1/2]
Defesa Civil:13:05 - Chuva na regiao de Campos do Jordao. Tem raios e vento. Atinge municipios vizinhos. Tenha cuidado nas proximas horas.

[DEFESA CIVIL 2/2]
Siga as orientações da defesa civil local e do plano de contingência municipal. Em caso de emergência, ligue 199 ou 193.
```

A fragmentação existe somente para adequar o conteúdo ao transporte pela rede.

## Testes

Os testes podem ser executados individualmente:

```bash
python3 tests/teste_deduplicacao.py
python3 tests/teste_update_cancel.py
python3 tests/teste_update_fora.py
python3 tests/teste_expiracao.py
python3 tests/teste_localizacao.py
```

Os testes cobrem, entre outros pontos:

* deduplicação entre execuções;
* atualização de alertas;
* cancelamento de alertas;
* atualização que deixa de atingir a localização;
* expiração;
* filtragem geográfica;
* processamento de múltiplos polígonos;
* localização sem alerta correspondente.

O projeto também contém ferramentas auxiliares para inspeção e desenvolvimento:

```text
tools/debug_cap.py
tools/defesa_civil_test.py
tools/teste1.py
```

## Execução

Torne o programa executável:

```bash
chmod +x defesa_civil_alertas.py
```

Execute:

```bash
./defesa_civil_alertas.py
```

A aplicação consulta o feed, processa os alertas e acompanha continuamente os eventos que atingem a localização configurada.

Durante condições sem novos alertas relevantes, o gateway permanece em monitoramento sem gerar transmissões desnecessárias.

O uso de `systemd` para reiniciar automaticamente o programa após uma falha é opcional e não faz parte da configuração padrão do projeto.

## Dependências

O projeto utiliza Python 3 e a biblioteca:

```text
requests
```

Instalação:

```bash
python3 -m pip install requests
```

Em sistemas onde o `pip` global é bloqueado, recomenda-se utilizar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

## Segurança e privacidade

As coordenadas utilizadas para determinar a área afetada são processadas localmente.

O projeto não publica automaticamente latitude ou longitude como parte da mensagem de alerta.

O arquivo:

```text
defesa_civil_state.json
```

também permanece local e não deve ser versionado.

## Integração Meshtastic

A camada de processamento foi desenvolvida separadamente da camada de rádio.

Atualmente, o programa prepara e exibe as mensagens, mas a transmissão física pela rede Meshtastic ainda não está integrada.

A arquitetura prevista é:

```text
Defesa Civil
     |
     v
Linux / Gateway
     |
     | Wi-Fi
     v
Nó Meshtastic
     |
     | LoRa
     v
Rede Meshtastic
```

A integração com o hardware será implementada posteriormente, após a disponibilidade e os testes do nó Meshtastic utilizado pelo projeto.

## Princípio do projeto

O gateway foi projetado para ser **event-driven**.

Em condições normais:

```text
Sem alerta relevante
        |
        v
     Silêncio
```

Quando existe um alerta oficial que afeta a localização:

```text
Alerta oficial
      |
      v
Área afetada
      |
      v
Localização atingida
      |
      v
Novo ou atualizado
      |
      v
Retransmissão
```

Isso reduz o uso desnecessário da rede LoRa e evita transformar o gateway em uma fonte constante de mensagens.

## Estrutura do projeto

```text
defesa-civil-meshtastic-gateway/
│
├── config.py
├── defesa_civil_alertas.py
├── defesa_civil_localizacao.py
│
├── tests/
│   ├── teste_deduplicacao.py
│   ├── teste_expiracao.py
│   ├── teste_localizacao.py
│   ├── teste_update_cancel.py
│   └── teste_update_fora.py
│
├── tools/
│   ├── debug_cap.py
│   ├── defesa_civil_test.py
│   └── teste1.py
│
├── .gitignore
├── LICENSE
└── README.md
```

Arquivos gerados durante a execução, como:

```text
defesa_civil_state.json
__pycache__/
```

não fazem parte do repositório.

## Status

**Em desenvolvimento**

A camada de aquisição, interpretação, filtragem geográfica, deduplicação, retenção do estado e preparação das mensagens está em desenvolvimento ativo.

A integração com o hardware Meshtastic e a transmissão LoRa serão adicionadas em uma etapa posterior.

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo `LICENSE` para o texto completo.

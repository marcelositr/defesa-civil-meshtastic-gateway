# Defesa Civil Meshtastic Gateway

Gateway de alertas oficiais da Defesa Civil para redes Meshtastic.

O projeto consulta o feed oficial de alertas no padrão **CAP (Common Alerting Protocol)**, verifica se a localização configurada está dentro da área geográfica do alerta e prepara a mensagem oficial para retransmissão pela rede Meshtastic.

O objetivo é manter a rede silenciosa durante condições normais e transmitir somente alertas oficiais que realmente atingem a área monitorada.

## Objetivos

* Consultar automaticamente o feed oficial da Defesa Civil.
* Interpretar alertas no padrão CAP 1.2.
* Verificar a área afetada utilizando os polígonos fornecidos pelo alerta.
* Comparar os polígonos com a localização do gateway.
* Evitar retransmissões duplicadas.
* Detectar atualizações e cancelamentos de alertas.
* Ignorar alertas expirados.
* Preservar o texto oficial da Defesa Civil.
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
     Novo / Atualização
            |
            v
     Mensagem oficial
            |
            v
       Meshtastic
```

## Fonte dos alertas

O projeto utiliza o feed oficial da Defesa Civil disponibilizado pelo Ministério da Integração e do Desenvolvimento Regional:

```text
https://idapfile.mdr.gov.br/idap/api/rss/cap
```

O conteúdo é processado no padrão **CAP 1.2**.

A aplicação não depende do nome do município presente em `areaDesc` para determinar se um alerta atinge a localização.

A área geográfica é determinada pelos polígonos fornecidos no próprio alerta CAP.

## Filtragem geográfica

Cada alerta pode conter um ou mais polígonos.

O gateway utiliza as coordenadas configuradas para verificar se o ponto está dentro de pelo menos um desses polígonos.

Atualmente existem dois modos previstos:

```text
manual
gps
```

### Modo manual

Utiliza coordenadas definidas na configuração:

```python
LOCATION_MODE = "manual"

LOCATION_NAME = "Campos do Jordão"

LOCATION_LAT = -22.739
LOCATION_LON = -45.591
```

Esse modo é adequado para um gateway instalado em uma localização fixa.

### Modo GPS

A estrutura para utilização do GPS do nó Meshtastic já está prevista, mas a integração com o hardware ainda será implementada.

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

Alertas expirados são descartados antes da retransmissão.

Atualizações são relacionadas aos alertas anteriores por meio das referências CAP.

Cancelamentos tornam o alerta referenciado inativo no estado local.

## Deduplicação

O gateway mantém um estado local em:

```text
defesa_civil_state.json
```

Esse arquivo registra informações necessárias para impedir que o mesmo alerta seja retransmitido repetidamente.

A identificação não depende somente do `identifier`.

Uma assinatura SHA-256 também é criada utilizando campos relevantes do alerta para permitir a detecção de alterações no mesmo alerta.

O arquivo de estado é deliberadamente ignorado pelo Git:

```gitignore
defesa_civil_state.json
```

Cada instalação possui seu próprio estado local.

## Mensagem oficial

O projeto não resume nem reescreve a mensagem da Defesa Civil.

O conteúdo principal utilizado é:

```text
headline
```

e, quando disponível, a orientação oficial:

```text
instruction
```

A `description` não é retransmitida quando ela apenas duplica o `headline`, comportamento observado no feed oficial.

O conteúdo oficial não recebe:

* resumo automático;
* interpretação;
* classificação própria;
* alteração de significado;
* truncamento;
* informações inventadas pelo gateway.

A única alteração prevista é a estrutura necessária para transporte pela rede, como a divisão de uma mensagem longa.

## Fragmentação para Meshtastic

Mensagens maiores que o limite configurado são divididas em partes.

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

## Estado atual

O processamento do feed e a lógica de filtragem já foram testados com dados reais do feed da Defesa Civil.

Testes realizados incluem:

* deduplicação entre execuções;
* atualização de alertas;
* cancelamento de alertas;
* atualização que deixa de atingir a localização;
* expiração;
* filtragem geográfica;
* processamento de múltiplos polígonos;
* localização sem alerta correspondente.

O feed também foi testado com diferentes localidades para validar o filtro geográfico.

## Testes

Os testes podem ser executados individualmente:

```bash
./teste_deduplicacao.py
./teste_update_cancel.py
./teste_update_fora.py
./teste_expiracao.py
./teste_localizacao.py
```

O projeto também contém ferramentas auxiliares para inspeção e desenvolvimento:

```text
debug_cap.py
defesa_civil_test.py
teste1.py
defesa_civil_localizacao.py
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

A aplicação consulta o feed, processa os alertas e exibe os eventos que atingem a localização configurada.

Durante condições sem novos alertas relevantes, o gateway não precisa transmitir mensagens pela rede.

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
├── defesa_civil_alertas.py
├── defesa_civil_localizacao.py
├── defesa_civil_test.py
├── debug_cap.py
│
├── teste1.py
├── teste_deduplicacao.py
├── teste_expiracao.py
├── teste_localizacao.py
├── teste_update_cancel.py
├── teste_update_fora.py
│
├── .gitignore
└── README.md
```

Arquivos gerados durante a execução, como:

```text
defesa_civil_state.json
__pycache__/
```

não fazem parte do repositório.

## Licença

A licença do projeto ainda não foi definida.

## Status

**Em desenvolvimento**

A camada de aquisição, interpretação, filtragem geográfica, deduplicação e preparação das mensagens está em desenvolvimento ativo.

A integração com o hardware Meshtastic e a transmissão LoRa serão adicionadas em uma etapa posterior.

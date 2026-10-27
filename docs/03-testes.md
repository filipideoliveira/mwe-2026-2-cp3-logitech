# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 25 (≈ 80%) | Política de Compensação (faixas, multiplicador, teto, arredondamento), cálculo do atraso, avaliação de ausência (geocerca e janela), retentativas de notificação e escolha de canal |
| Integração | 3 (≈ 10%) | Idempotência com banco real (RF09), numeração concorrente de notas (RNF03) e durabilidade da confirmação no broker (RNF01) |
| Ponta a ponta | 3 (≈ 10%) | Fluxo completo da confirmação até a nota emitida (RNF02), Portal ao vivo (RF10) e subida do ambiente com um comando (RNF04) |

**Por que essa proporção:** o maior risco da Garantia de Prazo está nas regras de cálculo,
que têm muitos valores-limite (3 faixas × 2 limites × 3 tipos de cliente × teto). Essas regras
são funções puras: rodam em milissegundos e não dependem de infraestrutura, então ficam
na base da pirâmide. A integração aparece só onde um dublê **esconderia** o defeito:
concorrência, constraint de unicidade e reentrega do broker só se comportam de verdade com
banco e broker reais. Os testes ponta a ponta são poucos porque são lentos e frágeis. Eles
validam o que só existe com o sistema inteiro rodando: o tempo de 5 min, a atualização ao
vivo e o `docker compose up`.

## Decisões sobre ambiguidades dos requisitos

| Ponto ambíguo | Requisito | Decisão adotada no plano |
|---|---|---|
| "Atraso medido em horas", mas os limites "até 2 h" e "acima de 2 h" exigem precisão | RF01, RF02 | O atraso é calculado em **minutos inteiros**. 2h00 (120 min) ainda está na faixa sem crédito; 2h01 (121 min) é o primeiro valor com crédito |
| Os limites de faixa são inclusivos? | RF02 | "Até X h" é **inclusivo** e "acima de X h" é **exclusivo**: 24h00 → 10%, 24h01 → 25%; 72h00 → 25%, 72h01 → 50% |
| Entrega antes do prazo gera atraso negativo | RF01 | Atraso ≤ 0 é tratado como **0** (entrega no prazo, sem crédito) |
| O teto vale antes ou depois de dobrar o percentual? | RF03 | O teto é aplicado **depois** do multiplicador: Corporativo acima de 72 h = 100% do frete, limitado a R$ 2.000 |
| O requisito não define o arredondamento | RF02 | Valores em centavos, com arredondamento **HALF_UP** para 2 casas |
| "Cortesia (frete zero)": é um tipo de cliente ou qualquer pedido com frete zero? | RF03 | **Cortesia é um tipo de cliente**. A regra dele é: crédito zero e notificação de atraso obrigatória |
| "Retentada até 3 vezes" | RF08 | **1 envio original + 3 retentativas = 4 tentativas** no máximo |
| "A até 200 m" e "pelo menos 10 min" são inclusivos? | RF05 | Os dois são **inclusivos**: 200 m e 10min00 comprovam a ausência; 201 m ou 9min59 não comprovam |
| "Sequencial e nunca repetido": pode haver lacunas? | RF06, RNF03 | O plano verifica que os números são **únicos e crescentes**. Lacunas (por exemplo, após um rollback) não são verificadas, porque o requisito não as proíbe |

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h00 (120 min) | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h01 (121 min) | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT03 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h00 (1.440 min) | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT04 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h01 (1.441 min) | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT05 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h00 (4.320 min) | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT06 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h01 (4.321 min) | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT07 | RF02 | Cliente Varejo, frete de R$ 1.000,00 | Atraso de 72h01 | Crédito de R$ 500,00 (exatamente no teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT08 | RF02 | Cliente Varejo, frete de R$ 1.000,02 | Atraso de 72h01 | Crédito de R$ 500,00 (50% = R$ 500,01, limitado ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT09 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 60,00 (20%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT10 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 24h01 | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT11 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 72h01 | Crédito de R$ 300,00 (100%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT12 | RF03 | Cliente Corporativo, frete de R$ 2.000,00 | Atraso de 72h01 | Crédito de R$ 2.000,00 (exatamente no teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT13 | RF03 | Cliente Corporativo, frete de R$ 2.000,02 | Atraso de 72h01 | Crédito de R$ 2.000,00 (100% = R$ 2.000,02, limitado ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT14 | RF02 | Cliente Varejo, frete de R$ 33,35 | Atraso de 2h01 | Crédito de R$ 3,34 (10% = 3,335, arredondado HALF_UP) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT15 | RF01 | Prazo Prometido 27/10 10:00 | Confirmação de entrega 27/10 09:00 | Atraso = 0; garantia `Cumprida`; crédito de R$ 0,00 | Unidade | Nenhum | Cálculo puro entre duas datas |
| CT16 | RF01 | Serviço de Frete informa Prazo Prometido 27/10 10:00 para o pedido | Confirmação de entrega 27/10 12:01, Varejo, frete de R$ 300,00 | Atraso de 121 min; crédito de R$ 30,00 | Unidade | Stub | O Frete só fornece o prazo; o caso verifica o cálculo, não a chamada ao Frete |
| CT17 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 30h | Crédito de R$ 0,00 e notificação de atraso enviada exatamente 1 vez | Unidade | Mock | O que se verifica é a interação: a porta de notificação precisa ser chamada mesmo sem crédito |
| CT18 | RF04 | Um tipo de cliente fictício "Parceiro" é registrado no registro de políticas dentro do teste | Pedido "Parceiro", atraso de 24h01 | O registro resolve a nova política; CT01 a CT13 continuam passando sem alteração nas classes Varejo, Corporativo e Cortesia | Unidade | Nenhum | Verifica a extensão por registro de uma nova política, sem dependência externa |
| CT19 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00 | Posições do veículo parado a 200 m do endereço das 13:50 às 14:00 (10min00) | Ausência comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT20 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00 | Posições do veículo parado a 201 m das 13:50 às 14:00 | Ausência **não** comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT21 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00:00 | Posições do veículo parado a 150 m das 13:50:01 às 14:00:00 (9min59) | Ausência **não** comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT22 | RF05 | Garantia ativa, Varejo, frete de R$ 300,00; Rastreamento publicou `AusenciaComprovada` | Confirmação de entrega com atraso de 30h | Garantia `Isenta`; nenhum evento `CreditoConcedido` publicado | Unidade | Spy | O spy registra os eventos publicados para conferir, depois da execução, que nenhum crédito saiu |
| CT23 | RF07 | Cliente com canal preferido WhatsApp | Evento `CreditoConcedido` de R$ 75,00 | API do parceiro chamada 1 vez com o payload no formato do parceiro; serviço de e-mail não chamado | Unidade | Mock | Verifica a interação e a tradução feita pelo Adapter sem depender da API externa |
| CT24 | RF08 | Gateway do canal falha nas 2 primeiras tentativas e responde com sucesso na 3ª | Envio de notificação | Notificação `Enviada`; exatamente 3 chamadas ao gateway; nada na fila de falhas | Unidade | Mock | O caso verifica o número de chamadas, que é uma interação |
| CT25 | RF08 | Gateway do canal falha em todas as tentativas | Envio de notificação | Exatamente 4 chamadas (1 + 3 retentativas); status `FalhaDefinitiva`; 1 mensagem na fila de falhas (DLQ) | Unidade | Stub (gateway) + Spy (DLQ) | O stub programa as falhas; o spy registra o que chegou à DLQ para provar que a falha não foi descartada |
| CT26 | RF09 | Garantia ativa, Varejo, frete de R$ 300,00; banco real (Testcontainers) | A mesma `EntregaConfirmada` (mesmo `entregaId`, atraso de 30h) consumida 2 vezes | Exatamente 1 crédito de R$ 75,00 no banco e 1 evento `CreditoConcedido` | Integração | Nenhum | A garantia vem da constraint `UNIQUE` do banco real; um dublê esconderia exatamente esse comportamento |
| CT27 | RF06, RNF03 | Faturamento com banco real (Testcontainers) | 1.000 emissões de nota de crédito concorrentes | 1.000 notas com números distintos e crescentes | Integração | Nenhum | Condição de corrida só aparece com banco e transações reais |
| CT28 | RNF01 | Broker real; consumidor da Garantia é derrubado antes do ack | `EntregaConfirmada` com atraso de 30h | A mensagem é reentregue após o consumidor voltar; exatamente 1 crédito gerado | Integração | Nenhum | Verifica a durabilidade do broker, que não existe num dublê |
| CT29 | RNF02 | Ambiente completo no ar; Varejo, frete de R$ 300,00 | Entregador confirma a entrega com 30h de atraso | Nota de crédito de R$ 75,00 emitida em até 5 min após a confirmação | Ponta a ponta | Nenhum | Mede o tempo real do fluxo entre os serviços |
| CT30 | RF10 | Ambiente completo no ar; cliente com o Portal aberto | Nova posição do veículo publicada; depois, crédito concedido | Mapa e previsão de chegada atualizados sem recarregar a página; saldo de créditos atualizado | Ponta a ponta | Nenhum | Verifica a atualização ao vivo de ponta a ponta no navegador |
| CT31 | RNF04 | Repositório recém-clonado | `docker compose up` | Todos os serviços em estado `healthy` | Ponta a ponta | Nenhum | Verifica a subida real dos contêineres |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Na primeira faixa, `atraso > 120` trocado por `atraso >= 120` | CT01 | Com 2h00, o mutante passa a dar R$ 30,00 em vez de R$ 0,00 |
| Na segunda faixa, `atraso > 1440` trocado por `atraso >= 1440` | CT03 | Com 24h00, o mutante passa a dar 25% (R$ 75,00) em vez de 10% (R$ 30,00) |
| Teto aplicado **antes** do multiplicador (ou teto do Varejo usado no Corporativo) | CT12, CT13 | O Corporativo com frete de R$ 2.000,00 retornaria R$ 1.000,00 (ou R$ 500,00) em vez de R$ 2.000,00 |
| `min(credito, teto)` trocado por `max(credito, teto)` | CT01, CT07 | Com atraso de 2h00, o crédito passaria a ser R$ 500,00 em vez de R$ 0,00 |
| Na geocerca, `distancia <= 200` trocado por `distancia < 200` | CT19 | A 200 m exatos, a ausência deixaria de ser comprovada |
| No laço de retentativas, `tentativas <= 3` trocado por `tentativas < 3` | CT25 | O gateway seria chamado 3 vezes em vez de 4 |
| Remoção da verificação de `entregaId` já processado | CT26 | A segunda entrega duplicada geraria um segundo crédito |

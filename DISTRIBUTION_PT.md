# Guia de Distribuição e Proteção do Windows (SmartScreen)

Ao distribuir um arquivo `.exe` gerado pelo PyInstaller, o Windows pode exibir um aviso de "O Windows protegeu o seu computador" (SmartScreen). Isso ocorre porque o executável não possui uma assinatura digital de um desenvolvedor conhecido.

Aqui estão as formas de resolver ou contornar isso:

## 1. Assinatura Digital (Solução Profissional)
A única forma de remover o aviso permanentemente para todos os usuários é assinar o arquivo com um **Certificado de Assinatura de Código** (Code Signing Certificate).
- **Custo:** Geralmente pago anualmente (ex: DigiCert, Sectigo).
- **Como funciona:** Você usa uma ferramenta como `signtool.exe` do Windows SDK para aplicar sua assinatura ao `.exe`.

## 2. Uso de Instaladores (Recomendado)
Em vez de distribuir um único `.exe`, use um criador de instaladores como **Inno Setup** ou **NSIS**.
- Instaladores costumam passar mais confiança aos sistemas de segurança do que arquivos executáveis avulsos.
- Eles também permitem criar atalhos no Menu Iniciar e Desktop de forma padronizada.

## 3. Construção de Reputação
O SmartScreen baseia-se na "Reputação". 
- Quanto mais pessoas baixarem e executarem o seu programa (clicando em "Mais informações" -> "Executar assim mesmo"), mais rápida será a construção da reputação.
- Eventualmente, o Windows deixará de exibir o aviso para esse arquivo específico.

## 4. Instruções para o Usuário (Solução Imediata)
Até que você tenha um certificado, a melhor forma é instruir o usuário:
1. Clique em **"Mais informações"**.
2. Clique no botão **"Executar assim mesmo"** que aparecerá.

## 5. Desbloqueio Manual
Se o Windows bloquear a execução completamente:
1. Clique com o botão direito no arquivo `.exe`.
2. Vá em **Propriedades**.
3. Na aba "Geral", marque a caixa **"Desbloquear"** (ao lado de Segurança) e clique em OK.

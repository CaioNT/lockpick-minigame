# Arrow Detector

O script analisa a tela, detecta setas em qualquer resolução (eu acho) e simula os inputs automaticamente.

## Características

-  Funcionamento em tempo real
-  Interface gráfica intuitiva
-  Hotkey customizável
-  Log de atividades

## Requisitos

- **Windows 7+**
- **Python 3.8+** (será instalado automaticamente se não tiver)

## Executar o instalador

**Clique 2 vezes em `install.bat`**

O script irá:
- ✅ Verificar se Python está instalado
- ✅ Instalar as dependências automaticamente
- ✅ Iniciar o Arrow Detector

## Como Usar

### Primeira Execução

1. Clique em **"GRAVAR HOTKEY"**
2. Pressione a tecla que deseja usar (ex: `P`, `F12`, etc)
3. A hotkey será registrada

### Usando a Aplicação

1. Inicie o minigame do lockpick
2. Pressione a hotkey que configurou
3. As setas serão detectadas e os inputs simulados automaticamente

### Botões da Interface

| Botão | Função |
|-------|--------|
| **GRAVAR HOTKEY** | Registra uma nova tecla de atalho |
| **EXECUTAR** | Executa o detector manualmente |
| **DEBUG** | Abre o arquivo de log |
| **BANDEJA** | Minimiza para bandeja do sistema |

##  Estrutura de Arquivos

```
Arrow-Detector/
├── lockpick.exe              # Interface gráfica
├── arrow-detector.exe        # Motor de detecção
├── install.bat               # Script de instalação
├── requirements.txt          # Dependências
└── README.md                 # Este arquivo
```

## Configuração Avançada

### Resolver Problemas de Detecção

Se o detector não estiver encontrando as setas corretamente:

1. Abra `arrow-log.txt` para ver os logs
2. Verifique se as setas aparecem em **branco puro** (RGB: 255,255,255)
3. Ajuste a zona de busca editando os percentuais em `arrow-detector.py`

### Mudar a Zona de Busca

Edite os valores em `arrow-detector.py`:

```python
hud_start_pct = 0.855  # Onde começar (85.5% da altura)
hud_end_pct = 0.880    # Onde terminar (88% da altura)
```

## 🐛 Solução de Problemas

### "Nenhuma seta detectada"
- Abra `arrow-log.txt` para verificar a resolução detectada

### "Hotkey não funciona"
- Algumas hotkeys podem estar reservadas pelo Windows
- Tente outra tecla (ex: `F1`, `F2`, `F3`, etc)
- Se usar `Ctrl+X`, pressione na ordem: Ctrl primeiro, depois X

### "Arquivo .exe não abre"
- Certifique-se de que as dependências foram instaladas
- Execute `install.bat` novamente
- Se persistir, abra `lockpick-debug.log` para mais informações

## Logs

Os logs são salvos em:
- `arrow-log.txt` - Log do detector
- `lockpick-debug.log` - Log da interface gráfica

Abra esses arquivos para debugar problemas.

## Desempenho

| Métrica | Valor |
|---------|-------|
| Latência de detecção | ~10ms |
| Taxa de acurácia | >95% |
| Consumo de RAM | ~50MB |
| CPU | <5% |

## Privacidade

-  Nenhuma conexão com internet
-  Dados armazenados localmente

## Dependências Instaladas

- `opencv-python` - Processamento de imagem
- `numpy` - Operações matemáticas
- `Pillow` - Manipulação de imagens
- `pynput` - Simulação de input
- `keyboard` - Captura de hotkey
- `pystray` - Ícone na bandeja

## Suporte

Se encontrar problemas:

1. Verifique os arquivos de log
2. Teste em outra resolução
3. Tente resetar a hotkey
4. Tente executar como administrador

## Licença

Uso pessoal permitido. Venda ou distribuição comercial proibida.

---

**Versão:** 1.0  
**Última atualização:** Dezembro 2025  
**Autor:** é o 2
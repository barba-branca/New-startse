# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-16

### Added
- **Real-time Ticker**: Implementação de ticker financeiro em tempo real usando JavaScript puro (sem dependências de backend).
- **Multi-API Integration**: Integração com Binance API (Cripto) e AwesomeAPI (Câmbio) para dados atualizados.
- **Developer Branding**: Adicionada a assinatura "Produzido por Develops Code" em todas as páginas e no README.

### Changed
- **Global Rebranding**: O projeto foi oficialmente renomeado de "STARTSE" para **New Start-se** em todo o frontend, títulos e documentação.
- **Frontend Decoupling**: Removida a dependência do `yfinance` no backend para evitar erros de DLL no Windows, movendo a lógica para o lado do cliente.

### Fixed
- **Estabilização do Servidor**: Implementados stubs e mocks para bibliotecas bloqueadas pelo Windows App Control, garantindo que o `runserver` opere sem travamentos.

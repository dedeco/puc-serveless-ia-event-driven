#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

function show_menu() {
    clear
    echo -e "${BLUE}=============================================================="
    echo -e "         AULA 06: SERVERLESS E INTELIGÊNCIA ARTIFICIAL"
    echo -e "==============================================================${NC}"
    echo "1) Step 01 - Integração Base com Vertex AI & Gemini"
    echo "2) Step 02 - Function Calling (Declarando Ferramentas)"
    echo "3) Step 03 - O Loop ReAct (Orquestração de Agentes)"
    echo "4) Step 04 - Agente DevOps Orientado a Eventos Completo"
    echo "q) Sair"
    echo "--------------------------------------------------------------"
}

function run_step() {
    STEP_DIR=$1
    README_PATH="lab/$STEP_DIR/README.md"
    
    clear
    echo -e "${GREEN}>>> Entrando no $STEP_DIR...${NC}"
    
    if [ -f "$README_PATH" ]; then
        echo -e "${BLUE}Instruções do Laboratório:${NC}"
        cat "$README_PATH"
        echo -e "\n--------------------------------------------------------------"
    fi
    
    echo "Pressione ENTER para entrar no diretório do laboratório ou Ctrl+C para voltar."
    read
    cd "lab/$STEP_DIR"
    exec bash
}

while true; do
    show_menu
    read -p "Escolha uma opção: " opt
    case $opt in
        1) run_step "step-01-base" ;;
        2) run_step "step-02-tools" ;;
        3) run_step "step-03-react" ;;
        4) run_step "step-04-full" ;;
        q) exit ;;
        *) echo "Opção inválida." ; sleep 1 ;;
    esac
done

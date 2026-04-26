// frontend/script.js
let sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
let idiomaForcado = null;
let modoAprendizado = false;
let ultimaPergunta = null;
let ultimoIdioma = null;

// DOM elements
const messagesArea = document.getElementById('messages-area');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const btnBackup = document.getElementById('btn-backup');
const btnLimparChat = document.getElementById('btn-limpar-chat');
const btnAtualizarStats = document.getElementById('btn-atualizar-stats');
const modal = document.getElementById('backup-modal');
const modalOk = document.getElementById('modal-ok');
const closeModal = document.querySelector('.close');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarEstatisticas();
    setupLanguageButtons();
    setupEventListeners();
});

function setupLanguageButtons() {
    const langBtns = document
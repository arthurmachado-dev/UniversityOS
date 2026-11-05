/* Funções globais compartilhadas entre as páginas. */

function escapeHtml(texto) {
    return String(texto ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
}

/** Recarrega os dados da página atual, se ela expuser uma função de carga conhecida. */
function recarregarPaginaAtual() {
    ['loadDashboard', 'loadFaltas'].forEach(nome => {
        if (typeof window[nome] === 'function') window[nome]();
    });
}

async function openModalFalteiHoje() {
    const modal = document.getElementById('modal-faltei-hoje');
    const lista = document.getElementById('lista-faltei-hoje');
    if (!modal || !lista) return;
    modal.classList.remove('hidden');
    lista.innerHTML = '<p class="text-sm text-on-surface-variant">Carregando disciplinas...</p>';
    try {
        const res = await fetch('/api/disciplinas');
        const disciplinas = await res.json();
        if (!Array.isArray(disciplinas) || disciplinas.length === 0) {
            lista.innerHTML = '<p class="text-sm text-on-surface-variant">Nenhuma disciplina cadastrada.</p>';
            return;
        }
        lista.innerHTML = disciplinas.map(d => `
            <label class="flex items-center gap-3 p-3 rounded-xl border border-outline-variant/60 hover:bg-surface-container-low cursor-pointer">
                <input type="checkbox" value="${escapeHtml(d.id)}" class="chk-faltei rounded border-outline text-primary w-4 h-4">
                <span class="text-sm font-semibold">${escapeHtml(d.nome)}</span>
            </label>`).join('');
    } catch (e) {
        lista.innerHTML = '<p class="text-sm text-error">Não foi possível carregar as disciplinas.</p>';
    }
}

function closeModalFalteiHoje() {
    document.getElementById('modal-faltei-hoje')?.classList.add('hidden');
}

async function confirmarFalteiHoje() {
    const ids = Array.from(document.querySelectorAll('.chk-faltei:checked')).map(c => c.value);
    if (ids.length === 0) { closeModalFalteiHoje(); return; }
    try {
        await Promise.all(ids.map(id => fetch('/api/faltas/incrementar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ disciplina_id: id, quantidade: 1 })
        })));
        closeModalFalteiHoje();
        recarregarPaginaAtual();
    } catch (e) {
        alert('Erro ao registrar as faltas.');
    }
}

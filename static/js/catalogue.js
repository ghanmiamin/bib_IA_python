/* ════════════════════════════════════════════
   CATALOGUE.JS — CRUD des Livres
   ════════════════════════════════════════════ */

let currentFilter  = 'tous';
let deleteTargetId = null;
let searchTimeout  = null;

/* ─── TOAST ─── */
function showToast(msg, type = 'success') {
  const t = document.getElementById('app-toast');
  t.textContent = msg;
  t.className = `app-toast toast-${type} show`;
  setTimeout(() => t.classList.remove('show'), 3200);
}

/* ─── MODALS ─── */
function openModal(id) {
  document.getElementById(id).classList.add('open');
  lucide.createIcons();
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function closeOnOverlay(e, id) {
  if (e.target.id === id) closeModal(id);
}

/* ════════════════════════════════════════════
   RECHERCHE DYNAMIQUE
   ════════════════════════════════════════════ */
const searchInput = document.getElementById('search-input');
const btnClear    = document.getElementById('btn-clear');

searchInput.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  btnClear.style.display = searchInput.value ? 'flex' : 'none';
  searchTimeout = setTimeout(() => loadTable(searchInput.value), 300);
});

function clearSearch() {
  searchInput.value = '';
  btnClear.style.display = 'none';
  loadTable('');
}

/* ─── FILTRE PAR STATUT ─── */
function filterStatut(btn, statut) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentFilter = statut;
  applyFilter();
}

function applyFilter() {
  const rows = document.querySelectorAll('#books-tbody tr[data-statut]');
  let count = 0;
  rows.forEach(row => {
    const match = currentFilter === 'tous' || row.dataset.statut === currentFilter;
    row.style.display = match ? '' : 'none';
    if (match) count++;
  });
  document.getElementById('table-count').textContent = `${count} livre(s)`;
}

/* ─── CHARGER TABLE VIA API ─── */
async function loadTable(terme = '') {
  const url = terme ? `/api/livres?q=${encodeURIComponent(terme)}` : '/api/livres';
  const res  = await fetch(url);
  const data = await res.json();
  renderTable(data);
  updateStats();
}

function renderTable(livres) {
  const tbody = document.getElementById('books-tbody');
  if (!livres.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty-row">📭 Aucun livre trouvé</td></tr>';
    document.getElementById('table-count').textContent = '0 livre(s)';
    return;
  }

  const statutBadge = s => {
    if (s === 'disponible') return `<span class="statut-badge statut-dispo">✅ disponible</span>`;
    if (s === 'emprunté')   return `<span class="statut-badge statut-emprunte">📤 emprunté</span>`;
    return                         `<span class="statut-badge statut-reserve">🔖 réservé</span>`;
  };

  tbody.innerHTML = livres.map(l => `
    <tr data-statut="${l.statut}" data-id="${l.id_livre}">
      <td><span class="id-badge">#${l.id_livre}</span></td>
      <td><strong>${escHtml(l.titre)}</strong></td>
      <td>${escHtml(l.auteur)}</td>
      <td><span class="cat-badge">${escHtml(l.categorie)}</span></td>
      <td>${l.annee_publication}</td>
      <td>${l.quantite_disponible}</td>
      <td>${statutBadge(l.statut)}</td>
      <td>
        <div class="action-btns">
          <button class="btn-icon btn-edit" title="Modifier"
                  onclick="openEdit(${l.id_livre})">
            <i data-lucide="pencil"></i>
          </button>
          <button class="btn-icon btn-delete" title="Supprimer"
                  onclick="confirmDelete(${l.id_livre}, '${escHtml(l.titre).replace(/'/g,"\\'")}')">
            <i data-lucide="trash-2"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');

  lucide.createIcons();
  document.getElementById('table-count').textContent = `${livres.length} livre(s)`;
  applyFilter();
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ─── STATS ─── */
async function updateStats() {
  const res  = await fetch('/api/stats');
  const data = await res.json();
  document.getElementById('stat-total').textContent   = data.total;
  document.getElementById('stat-dispo').textContent   = data.disponibles;
  document.getElementById('stat-emprunte').textContent = data.empruntes;
  document.getElementById('stat-reserve').textContent  = data.reserves;
  document.getElementById('stat-auteurs').textContent  = data.auteurs;
}

/* ════════════════════════════════════════════
   AJOUTER
   ════════════════════════════════════════════ */
async function submitAdd() {
  const titre    = document.getElementById('add-titre').value.trim();
  const auteur   = document.getElementById('add-auteur').value.trim();
  const categorie = document.getElementById('add-categorie').value.trim();
  const annee    = document.getElementById('add-annee').value || 2024;
  const quantite = document.getElementById('add-quantite').value || 1;
  const statut   = document.getElementById('add-statut').value;

  if (!titre || !auteur || !categorie) {
    showToast('⚠ Titre, auteur et catégorie sont obligatoires.', 'error');
    return;
  }

  const res = await fetch('/api/livres', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ titre, auteur, categorie,
                           annee_publication: Number(annee),
                           quantite_disponible: Number(quantite), statut })
  });

  if (res.ok) {
    closeModal('modal-add');
    clearAddForm();
    await loadTable(searchInput.value);
    showToast('✅ Livre ajouté avec succès !', 'success');
  } else {
    showToast('❌ Erreur lors de l\'ajout.', 'error');
  }
}

function clearAddForm() {
  ['add-titre','add-auteur','add-categorie'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('add-annee').value = '';
  document.getElementById('add-quantite').value = 1;
  document.getElementById('add-statut').value = 'disponible';
}

/* ════════════════════════════════════════════
   MODIFIER
   ════════════════════════════════════════════ */
async function openEdit(id) {
  const res  = await fetch(`/api/livres/${id}`);
  if (!res.ok) { showToast('Livre introuvable.', 'error'); return; }
  const l = await res.json();

  document.getElementById('edit-id').value       = l.id_livre;
  document.getElementById('edit-titre').value    = l.titre;
  document.getElementById('edit-auteur').value   = l.auteur;
  document.getElementById('edit-categorie').value = l.categorie;
  document.getElementById('edit-annee').value    = l.annee_publication;
  document.getElementById('edit-quantite').value = l.quantite_disponible;
  document.getElementById('edit-statut').value   = l.statut;

  openModal('modal-edit');
}

async function submitEdit() {
  const id = document.getElementById('edit-id').value;
  const body = {
    titre:               document.getElementById('edit-titre').value.trim(),
    auteur:              document.getElementById('edit-auteur').value.trim(),
    categorie:           document.getElementById('edit-categorie').value.trim(),
    annee_publication:   Number(document.getElementById('edit-annee').value),
    quantite_disponible: Number(document.getElementById('edit-quantite').value),
    statut:              document.getElementById('edit-statut').value,
  };

  if (!body.titre || !body.auteur) {
    showToast('⚠ Titre et auteur sont obligatoires.', 'error');
    return;
  }

  const res = await fetch(`/api/livres/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (res.ok) {
    closeModal('modal-edit');
    await loadTable(searchInput.value);
    showToast('✅ Livre mis à jour !', 'success');
  } else {
    showToast('❌ Erreur lors de la mise à jour.', 'error');
  }
}

/* ════════════════════════════════════════════
   SUPPRIMER
   ════════════════════════════════════════════ */
function confirmDelete(id, titre) {
  deleteTargetId = id;
  document.getElementById('delete-livre-titre').textContent = `« ${titre} »`;
  openModal('modal-delete');
}

async function submitDelete() {
  if (!deleteTargetId) return;
  const res = await fetch(`/api/livres/${deleteTargetId}`, { method: 'DELETE' });
  if (res.ok) {
    closeModal('modal-delete');
    await loadTable(searchInput.value);
    showToast('🗑 Livre supprimé.', 'success');
  } else {
    showToast('❌ Erreur lors de la suppression.', 'error');
  }
  deleteTargetId = null;
}

/* ─── INIT ─── */
applyFilter();

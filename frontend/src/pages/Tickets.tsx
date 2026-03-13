import React, { useEffect, useState, useCallback } from 'react';
import client from '../api/client';
import { Ticket, TicketListResponse } from '../types';

const S: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  filterBar: { display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px', alignItems: 'center' },
  select: { padding: '7px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '13px' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: '24px' },
  th: { background: '#1e3a5f', color: '#fff', padding: '10px 12px', textAlign: 'left', fontSize: '13px' },
  td: { padding: '9px 12px', borderBottom: '1px solid #eef0f3', fontSize: '13px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  btnAI: { background: '#9c27b0', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  error: { background: '#fdecea', color: '#c62828', padding: '10px', borderRadius: '4px', marginBottom: '12px' },
  formCard: { background: '#fff', borderRadius: '8px', padding: '24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', maxWidth: '500px' },
  formTitle: { fontSize: '16px', fontWeight: 700, color: '#1e3a5f', marginBottom: '16px' },
  label: { display: 'block', fontSize: '13px', fontWeight: 600, color: '#444', marginBottom: '4px' },
  input: { width: '100%', padding: '8px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px' },
  textarea: { width: '100%', padding: '8px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px', resize: 'vertical', minHeight: '80px' },
  btnSubmit: { background: '#1a73e8', color: '#fff', border: 'none', padding: '9px 20px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px', fontWeight: 600 },
  pagination: { display: 'flex', gap: '8px', marginTop: '16px', alignItems: 'center', justifyContent: 'flex-end' },
  pageBtn: { padding: '6px 12px', border: '1px solid #cdd5e0', borderRadius: '4px', cursor: 'pointer', background: '#fff', fontSize: '13px' },
  pageBtnActive: { background: '#1a73e8', color: '#fff', border: '1px solid #1a73e8' },
};

const PAGE_SIZE = 20;

const Tickets: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ category: '', student_cnic: '', query: '' });
  const [submitting, setSubmitting] = useState(false);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = { page, size: PAGE_SIZE };
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;
      const res = await client.get<TicketListResponse>('/tickets/', { params });
      setTickets(res.data.items);
      setTotal(res.data.total);
      setError('');
    } catch {
      setError('Failed to load tickets.');
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, categoryFilter]);

  useEffect(() => { fetchTickets(); }, [fetchTickets]);

  const getAIReply = async (id: number) => {
    try {
      await client.post(`/tickets/${id}/ai-reply`);
      fetchTickets();
    } catch {
      setError('Failed to get AI reply.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await client.post('/tickets/', form);
      setForm({ category: '', student_cnic: '', query: '' });
      fetchTickets();
    } catch {
      setError('Failed to create ticket.');
    } finally {
      setSubmitting(false);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <h2 style={S.heading}>Tickets</h2>
      {error && <div style={S.error}>{error}</div>}

      <div style={S.filterBar}>
        <select style={S.select} value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Statuses</option>
          <option value="Open">Open</option>
          <option value="Resolved">Resolved</option>
          <option value="Pending">Pending</option>
        </select>
        <select style={S.select} value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          <option value="Data">Data</option>
          <option value="Exam">Exam</option>
          <option value="Registration">Registration</option>
          <option value="Other">Other</option>
        </select>
      </div>

      {loading ? <p>Loading…</p> : (
        <table style={S.table}>
          <thead>
            <tr>
              {['Category', 'Student CNIC', 'Query', 'AI Reply', 'Status', 'Actions'].map((h) => (
                <th key={h} style={S.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickets.length ? tickets.map((t) => (
              <tr key={t.id}>
                <td style={S.td}>{t.category}</td>
                <td style={S.td}>{t.student_cnic}</td>
                <td style={{ ...S.td, maxWidth: '200px' }} title={t.query}>{t.query}</td>
                <td style={{ ...S.td, maxWidth: '200px' }} title={t.ai_reply ?? ''}>{t.ai_reply ?? '—'}</td>
                <td style={S.td}>{t.status}</td>
                <td style={S.td}>
                  {t.status !== 'Resolved' && (
                    <button style={S.btnAI} onClick={() => getAIReply(t.id)}>Get AI Reply</button>
                  )}
                </td>
              </tr>
            )) : (
              <tr><td style={S.td} colSpan={6}>No tickets found.</td></tr>
            )}
          </tbody>
        </table>
      )}

      <div style={S.pagination}>
        <span style={{ fontSize: '13px', color: '#666' }}>{total} total</span>
        <button style={S.pageBtn} disabled={page === 1} onClick={() => setPage((p) => p - 1)}>← Prev</button>
        {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map((p) => (
          <button key={p} style={{ ...S.pageBtn, ...(p === page ? S.pageBtnActive : {}) }} onClick={() => setPage(p)}>{p}</button>
        ))}
        <button style={S.pageBtn} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next →</button>
      </div>

      <div style={S.formCard}>
        <div style={S.formTitle}>Create New Ticket</div>
        <form onSubmit={handleSubmit}>
          <label style={S.label}>Category</label>
          <select style={{ ...S.input }} value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} required>
            <option value="">Select category…</option>
            <option value="Data">Data</option>
            <option value="Exam">Exam</option>
            <option value="Registration">Registration</option>
            <option value="Other">Other</option>
          </select>
          <label style={S.label}>Student CNIC</label>
          <input style={S.input} value={form.student_cnic} onChange={(e) => setForm((f) => ({ ...f, student_cnic: e.target.value }))} required placeholder="e.g. 35202-1234567-1" />
          <label style={S.label}>Query</label>
          <textarea style={S.textarea} value={form.query} onChange={(e) => setForm((f) => ({ ...f, query: e.target.value }))} required placeholder="Describe the issue…" />
          <button style={S.btnSubmit} type="submit" disabled={submitting}>{submitting ? 'Submitting…' : 'Submit Ticket'}</button>
        </form>
      </div>
    </div>
  );
};

export default Tickets;

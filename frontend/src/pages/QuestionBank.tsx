import React, { useEffect, useState, useCallback } from 'react';
import client from '../api/client';
import { Question, QuestionListResponse } from '../types';

const S: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: '24px' },
  th: { background: '#1e3a5f', color: '#fff', padding: '10px 12px', textAlign: 'left', fontSize: '13px' },
  td: { padding: '9px 12px', borderBottom: '1px solid #eef0f3', fontSize: '13px' },
  error: { background: '#fdecea', color: '#c62828', padding: '10px', borderRadius: '4px', marginBottom: '12px' },
  formCard: { background: '#fff', borderRadius: '8px', padding: '24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', maxWidth: '560px', marginBottom: '24px' },
  formTitle: { fontSize: '16px', fontWeight: 700, color: '#1e3a5f', marginBottom: '16px' },
  label: { display: 'block', fontSize: '13px', fontWeight: 600, color: '#444', marginBottom: '4px' },
  input: { width: '100%', padding: '8px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px' },
  textarea: { width: '100%', padding: '8px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px', resize: 'vertical', minHeight: '80px' },
  btnSubmit: { background: '#1a73e8', color: '#fff', border: 'none', padding: '9px 20px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px', fontWeight: 600 },
  btnEdit: { background: '#ff6d00', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  pagination: { display: 'flex', gap: '8px', marginTop: '16px', alignItems: 'center', justifyContent: 'flex-end' },
  pageBtn: { padding: '6px 12px', border: '1px solid #cdd5e0', borderRadius: '4px', cursor: 'pointer', background: '#fff', fontSize: '13px' },
  pageBtnActive: { background: '#1a73e8', color: '#fff', border: '1px solid #1a73e8' },
  modalOverlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal: { background: '#fff', borderRadius: '8px', padding: '28px', width: '440px', boxShadow: '0 4px 24px rgba(0,0,0,0.15)' },
  modalTitle: { fontSize: '16px', fontWeight: 700, color: '#1e3a5f', marginBottom: '16px' },
  modalBtns: { display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '8px' },
  btnSave: { background: '#1a73e8', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' },
  btnCancel: { background: '#fff', color: '#333', border: '1px solid #cdd5e0', padding: '8px 18px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' },
};

const PAGE_SIZE = 20;

const QuestionBank: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ subject_area: '', teacher: '', question_text: '' });
  const [submitting, setSubmitting] = useState(false);
  const [editQ, setEditQ] = useState<Question | null>(null);
  const [editStatus, setEditStatus] = useState('');

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await client.get<QuestionListResponse>('/question-bank/', { params: { page, size: PAGE_SIZE } });
      setQuestions(res.data.items);
      setTotal(res.data.total);
      setError('');
    } catch {
      setError('Failed to load questions.');
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { fetchQuestions(); }, [fetchQuestions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await client.post('/question-bank/', form);
      setForm({ subject_area: '', teacher: '', question_text: '' });
      fetchQuestions();
    } catch {
      setError('Failed to add question.');
    } finally {
      setSubmitting(false);
    }
  };

  const openEdit = (q: Question) => {
    setEditQ(q);
    setEditStatus(q.review_status);
  };

  const handleSaveStatus = async () => {
    if (!editQ) return;
    try {
      await client.patch(`/question-bank/${editQ.id}`, { review_status: editStatus });
      setEditQ(null);
      fetchQuestions();
    } catch {
      setError('Failed to update review status.');
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <h2 style={S.heading}>Question Bank</h2>
      {error && <div style={S.error}>{error}</div>}

      <div style={S.formCard}>
        <div style={S.formTitle}>Add New Question</div>
        <form onSubmit={handleSubmit}>
          <label style={S.label}>Subject Area</label>
          <input style={S.input} value={form.subject_area} onChange={(e) => setForm((f) => ({ ...f, subject_area: e.target.value }))} required placeholder="e.g. Computer Science" />
          <label style={S.label}>Teacher</label>
          <input style={S.input} value={form.teacher} onChange={(e) => setForm((f) => ({ ...f, teacher: e.target.value }))} required placeholder="Teacher name" />
          <label style={S.label}>Question Text</label>
          <textarea style={S.textarea} value={form.question_text} onChange={(e) => setForm((f) => ({ ...f, question_text: e.target.value }))} required placeholder="Enter question…" />
          <button style={S.btnSubmit} type="submit" disabled={submitting}>{submitting ? 'Adding…' : 'Add Question'}</button>
        </form>
      </div>

      {loading ? <p>Loading…</p> : (
        <table style={S.table}>
          <thead>
            <tr>
              {['Subject Area', 'Teacher', 'Question Text', 'Review Status', 'Actions'].map((h) => (
                <th key={h} style={S.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {questions.length ? questions.map((q) => (
              <tr key={q.id}>
                <td style={S.td}>{q.subject_area}</td>
                <td style={S.td}>{q.teacher}</td>
                <td style={{ ...S.td, maxWidth: '300px' }}>{q.question_text}</td>
                <td style={S.td}>{q.review_status}</td>
                <td style={S.td}><button style={S.btnEdit} onClick={() => openEdit(q)}>Edit Status</button></td>
              </tr>
            )) : (
              <tr><td style={S.td} colSpan={5}>No questions found.</td></tr>
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

      {editQ && (
        <div style={S.modalOverlay}>
          <div style={S.modal}>
            <div style={S.modalTitle}>Update Review Status</div>
            <p style={{ fontSize: '13px', color: '#555', marginBottom: '12px' }}>{editQ.question_text}</p>
            <label style={S.label}>Review Status</label>
            <select style={{ ...S.input }} value={editStatus} onChange={(e) => setEditStatus(e.target.value)}>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
            <div style={S.modalBtns}>
              <button style={S.btnCancel} onClick={() => setEditQ(null)}>Cancel</button>
              <button style={S.btnSave} onClick={handleSaveStatus}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionBank;

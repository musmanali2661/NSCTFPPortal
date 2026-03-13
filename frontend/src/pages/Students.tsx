import React, { useEffect, useState, useCallback } from 'react';
import client from '../api/client';
import { Student, StudentListResponse } from '../types';

const S: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  filterBar: { display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px', alignItems: 'center' },
  select: { padding: '7px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '13px' },
  input: { padding: '7px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '13px', minWidth: '200px' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  th: { background: '#1e3a5f', color: '#fff', padding: '10px 12px', textAlign: 'left', fontSize: '13px', whiteSpace: 'nowrap' },
  td: { padding: '9px 12px', borderBottom: '1px solid #eef0f3', fontSize: '13px' },
  pending: { background: '#fff3cd' },
  bulk: { background: '#f8d7da' },
  btnEdit: { background: '#1a73e8', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', marginRight: '4px' },
  btnDel: { background: '#ea4335', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  pagination: { display: 'flex', gap: '8px', marginTop: '16px', alignItems: 'center', justifyContent: 'flex-end' },
  pageBtn: { padding: '6px 12px', border: '1px solid #cdd5e0', borderRadius: '4px', cursor: 'pointer', background: '#fff', fontSize: '13px' },
  pageBtnActive: { background: '#1a73e8', color: '#fff', border: '1px solid #1a73e8' },
  error: { background: '#fdecea', color: '#c62828', padding: '10px', borderRadius: '4px', marginBottom: '12px' },
  modalOverlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal: { background: '#fff', borderRadius: '8px', padding: '28px', width: '480px', boxShadow: '0 4px 24px rgba(0,0,0,0.15)' },
  modalTitle: { fontSize: '17px', fontWeight: 700, color: '#1e3a5f', marginBottom: '18px' },
  label: { display: 'block', fontSize: '13px', fontWeight: 600, color: '#444', marginBottom: '4px' },
  mInput: { width: '100%', padding: '8px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '14px', boxSizing: 'border-box', marginBottom: '12px' },
  modalBtns: { display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '8px' },
  btnSave: { background: '#1a73e8', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' },
  btnCancel: { background: '#fff', color: '#333', border: '1px solid #cdd5e0', padding: '8px 18px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' },
};

const PAGE_SIZE = 20;

const Students: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [department, setDepartment] = useState('');
  const [status, setStatus] = useState('');
  const [batchType, setBatchType] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editStudent, setEditStudent] = useState<Student | null>(null);
  const [editForm, setEditForm] = useState<Partial<Student>>({});
  const [saving, setSaving] = useState(false);

  const fetchStudents = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = { page, size: PAGE_SIZE };
      if (department) params.department = department;
      if (status) params.status = status;
      if (batchType) params.batch_type = batchType;
      if (search) params.search = search;
      const res = await client.get<StudentListResponse>('/students/', { params });
      setStudents(res.data.items);
      setTotal(res.data.total);
      setError('');
    } catch {
      setError('Failed to load students.');
    } finally {
      setLoading(false);
    }
  }, [page, department, status, batchType, search]);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this student?')) return;
    try {
      await client.delete(`/students/${id}`);
      fetchStudents();
    } catch {
      setError('Failed to delete student.');
    }
  };

  const openEdit = (s: Student) => {
    setEditStudent(s);
    setEditForm({ ...s });
  };

  const handleSave = async () => {
    if (!editStudent) return;
    setSaving(true);
    try {
      await client.put(`/students/${editStudent.id}`, editForm);
      setEditStudent(null);
      fetchStudents();
    } catch {
      setError('Failed to update student.');
    } finally {
      setSaving(false);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const rowStyle = (s: Student): React.CSSProperties => {
    if (s.status === 'Pending_Review') return S.pending;
    if (s.status === 'Bulk_Uploaded') return S.bulk;
    return {};
  };

  return (
    <div>
      <h2 style={S.heading}>Students</h2>
      {error && <div style={S.error}>{error}</div>}

      <div style={S.filterBar}>
        <input style={S.input} placeholder="Search name, reg no, CNIC…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
        <select style={S.select} value={department} onChange={(e) => { setDepartment(e.target.value); setPage(1); }}>
          <option value="">All Departments</option>
          <option value="CS">CS</option>
          <option value="IT">IT</option>
          <option value="SE">SE</option>
          <option value="EE">EE</option>
          <option value="ME">ME</option>
          <option value="CE">CE</option>
        </select>
        <select style={S.select} value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All Statuses</option>
          <option value="Validated">Validated</option>
          <option value="Pending_Review">Pending Review</option>
          <option value="Bulk_Uploaded">Bulk Uploaded</option>
          <option value="Student_Registered">Student Registered</option>
        </select>
        <select style={S.select} value={batchType} onChange={(e) => { setBatchType(e.target.value); setPage(1); }}>
          <option value="">All Batch Types</option>
          <option value="Morning">Morning</option>
          <option value="Evening">Evening</option>
        </select>
      </div>

      {loading ? (
        <p>Loading…</p>
      ) : (
        <table style={S.table}>
          <thead>
            <tr>
              {['Reg No', 'Full Name', 'Father Name', 'CNIC', 'Department', 'Batch Type', 'Status', 'Actions'].map((h) => (
                <th key={h} style={S.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {students.length ? students.map((s) => (
              <tr key={s.id} style={rowStyle(s)}>
                <td style={S.td}>{s.reg_no}</td>
                <td style={S.td}>{s.full_name}</td>
                <td style={S.td}>{s.father_name}</td>
                <td style={S.td}>{s.cnic}</td>
                <td style={S.td}>{s.department}</td>
                <td style={S.td}>{s.batch_type}</td>
                <td style={S.td}>{s.status}</td>
                <td style={S.td}>
                  <button style={S.btnEdit} onClick={() => openEdit(s)}>Edit</button>
                  <button style={S.btnDel} onClick={() => handleDelete(s.id)}>Delete</button>
                </td>
              </tr>
            )) : (
              <tr><td style={S.td} colSpan={8}>No students found.</td></tr>
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

      {editStudent && (
        <div style={S.modalOverlay}>
          <div style={S.modal}>
            <div style={S.modalTitle}>Edit Student</div>
            {(['full_name', 'father_name', 'cnic', 'department', 'batch_type', 'status'] as (keyof Student)[]).map((field) => (
              <div key={field}>
                <label style={S.label}>{field.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</label>
                <input
                  style={S.mInput}
                  value={String(editForm[field] ?? '')}
                  onChange={(e) => setEditForm((f) => ({ ...f, [field]: e.target.value }))}
                />
              </div>
            ))}
            <div style={S.modalBtns}>
              <button style={S.btnCancel} onClick={() => setEditStudent(null)}>Cancel</button>
              <button style={S.btnSave} onClick={handleSave} disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;

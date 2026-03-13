import React, { useEffect, useState, useCallback } from 'react';
import client from '../api/client';
import { Discrepancy, DiscrepancyListResponse } from '../types';

const S: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  filterBar: { display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px', alignItems: 'center' },
  select: { padding: '7px 10px', border: '1px solid #cdd5e0', borderRadius: '4px', fontSize: '13px' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  th: { background: '#1e3a5f', color: '#fff', padding: '10px 12px', textAlign: 'left', fontSize: '13px' },
  td: { padding: '9px 12px', borderBottom: '1px solid #eef0f3', fontSize: '13px' },
  error: { background: '#fdecea', color: '#c62828', padding: '10px', borderRadius: '4px', marginBottom: '12px' },
  btnResolve: { background: '#34a853', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  pagination: { display: 'flex', gap: '8px', marginTop: '16px', alignItems: 'center', justifyContent: 'flex-end' },
  pageBtn: { padding: '6px 12px', border: '1px solid #cdd5e0', borderRadius: '4px', cursor: 'pointer', background: '#fff', fontSize: '13px' },
  pageBtnActive: { background: '#1a73e8', color: '#fff', border: '1px solid #1a73e8' },
};

const severityBadge = (severity: string): React.CSSProperties => {
  const map: Record<string, React.CSSProperties> = {
    Critical: { background: '#ea4335', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700 },
    High: { background: '#ff6d00', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700 },
    Low: { background: '#fbbc04', color: '#333', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700 },
  };
  return map[severity] ?? { padding: '2px 8px', borderRadius: '12px', fontSize: '11px', background: '#e0e0e0' };
};

const PAGE_SIZE = 20;

const Discrepancies: React.FC = () => {
  const [items, setItems] = useState<Discrepancy[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [severity, setSeverity] = useState('');
  const [isResolved, setIsResolved] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = { page, size: PAGE_SIZE };
      if (severity) params.severity = severity;
      if (isResolved !== '') params.is_resolved = isResolved === 'true';
      const res = await client.get<DiscrepancyListResponse>('/discrepancies/', { params });
      setItems(res.data.items);
      setTotal(res.data.total);
      setError('');
    } catch {
      setError('Failed to load discrepancies.');
    } finally {
      setLoading(false);
    }
  }, [page, severity, isResolved]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const markResolved = async (id: number) => {
    try {
      await client.patch(`/discrepancies/${id}/resolve`);
      fetchData();
    } catch {
      setError('Failed to resolve discrepancy.');
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <h2 style={S.heading}>Discrepancies</h2>
      {error && <div style={S.error}>{error}</div>}

      <div style={S.filterBar}>
        <select style={S.select} value={severity} onChange={(e) => { setSeverity(e.target.value); setPage(1); }}>
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Low">Low</option>
        </select>
        <select style={S.select} value={isResolved} onChange={(e) => { setIsResolved(e.target.value); setPage(1); }}>
          <option value="">All</option>
          <option value="false">Unresolved</option>
          <option value="true">Resolved</option>
        </select>
      </div>

      {loading ? <p>Loading…</p> : (
        <table style={S.table}>
          <thead>
            <tr>
              {['Student Reg No', 'Student Name', 'Field Name', 'Error Type', 'Severity', 'Resolved', 'Actions'].map((h) => (
                <th key={h} style={S.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.length ? items.map((d) => (
              <tr key={d.id}>
                <td style={S.td}>{d.student_reg_no}</td>
                <td style={S.td}>{d.student_name}</td>
                <td style={S.td}>{d.field_name}</td>
                <td style={S.td}>{d.error_type}</td>
                <td style={S.td}><span style={severityBadge(d.severity)}>{d.severity}</span></td>
                <td style={S.td}>{d.is_resolved ? '✅ Yes' : '❌ No'}</td>
                <td style={S.td}>
                  {!d.is_resolved && (
                    <button style={S.btnResolve} onClick={() => markResolved(d.id)}>Mark Resolved</button>
                  )}
                </td>
              </tr>
            )) : (
              <tr><td style={S.td} colSpan={7}>No discrepancies found.</td></tr>
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
    </div>
  );
};

export default Discrepancies;

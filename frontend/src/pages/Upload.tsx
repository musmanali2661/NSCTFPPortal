import React, { useRef, useState } from 'react';
import client from '../api/client';
import { UploadResult } from '../types';

const S: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  card: { background: '#fff', borderRadius: '8px', padding: '28px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', maxWidth: '600px' },
  dropzone: {
    border: '2px dashed #1a73e8',
    borderRadius: '8px',
    padding: '40px',
    textAlign: 'center',
    color: '#1a73e8',
    cursor: 'pointer',
    marginBottom: '16px',
    background: '#f0f7ff',
    transition: 'background 0.15s',
  },
  dropzoneActive: { background: '#d0e8ff' },
  fileName: { marginBottom: '12px', fontSize: '13px', color: '#444' },
  btnRow: { display: 'flex', gap: '10px', marginBottom: '16px' },
  btnUpload: { background: '#1a73e8', color: '#fff', border: 'none', padding: '9px 20px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px', fontWeight: 600 },
  btnTemplate: { background: '#fff', color: '#1a73e8', border: '1px solid #1a73e8', padding: '9px 20px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' },
  error: { background: '#fdecea', color: '#c62828', padding: '10px', borderRadius: '4px', marginBottom: '12px' },
  resultBox: { background: '#f0f7ff', borderRadius: '6px', padding: '16px', marginTop: '16px' },
  resultTitle: { fontWeight: 700, color: '#1e3a5f', marginBottom: '8px' },
  statRow: { display: 'flex', gap: '20px', marginBottom: '12px' },
  statItem: { fontSize: '14px' },
  errList: { listStyle: 'none', padding: 0, margin: 0, maxHeight: '200px', overflowY: 'auto' },
  errItem: { padding: '4px 8px', background: '#fdecea', borderRadius: '4px', marginBottom: '4px', fontSize: '12px', color: '#c62828' },
};

const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setResult(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await client.post<UploadResult>('/uploads/csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = () => {
    const csv = 'reg_no,full_name,father_name,cnic,department,batch_type\n';
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'student_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <h2 style={S.heading}>Upload Student Data</h2>
      <div style={S.card}>
        <div
          style={{ ...S.dropzone, ...(dragOver ? S.dropzoneActive : {}) }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📂</div>
          <div style={{ fontWeight: 600 }}>Drag & drop CSV/XLSX here</div>
          <div style={{ fontSize: '12px', marginTop: '4px', color: '#666' }}>or click to browse</div>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files && setFile(e.target.files[0])}
          />
        </div>

        {file && <div style={S.fileName}>📄 {file.name} ({(file.size / 1024).toFixed(1)} KB)</div>}
        {error && <div style={S.error}>{error}</div>}

        <div style={S.btnRow}>
          <button style={{ ...S.btnUpload, opacity: (!file || uploading) ? 0.6 : 1 }} onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? 'Uploading…' : 'Upload'}
          </button>
          <button style={S.btnTemplate} onClick={handleDownloadTemplate}>⬇ Download Template</button>
        </div>

        {result && (
          <div style={S.resultBox}>
            <div style={S.resultTitle}>Upload Complete</div>
            <div style={S.statRow}>
              <span style={S.statItem}>✅ Created: <strong>{result.created}</strong></span>
              <span style={S.statItem}>🔄 Updated: <strong>{result.updated}</strong></span>
              <span style={S.statItem}>❌ Errors: <strong>{result.errors}</strong></span>
            </div>
            {result.row_errors?.length > 0 && (
              <>
                <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '6px', color: '#c62828' }}>Row Errors:</div>
                <ul style={S.errList}>
                  {result.row_errors.map((e, i) => (
                    <li key={i} style={S.errItem}>Row {e.row}: {e.message}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;

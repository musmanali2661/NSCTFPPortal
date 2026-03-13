import React, { useEffect, useState, useCallback } from 'react';
import client from '../api/client';
import { DashboardStats } from '../types';

const styles: Record<string, React.CSSProperties> = {
  heading: { fontSize: '20px', fontWeight: 700, color: '#1e3a5f', marginBottom: '20px' },
  sectionLabel: { fontSize: '14px', fontWeight: 600, color: '#555', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: '16px', marginBottom: '28px' },
  card: {
    background: '#fff',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
    borderLeft: '4px solid #1a73e8',
  },
  cardValue: { fontSize: '32px', fontWeight: 700, color: '#1e3a5f' },
  cardLabel: { fontSize: '12px', color: '#666', marginTop: '4px' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  th: { background: '#1e3a5f', color: '#fff', padding: '10px 14px', textAlign: 'left', fontSize: '13px' },
  td: { padding: '10px 14px', borderBottom: '1px solid #eef0f3', fontSize: '14px' },
  refreshNote: { fontSize: '12px', color: '#888', marginBottom: '16px' },
  error: { background: '#fdecea', color: '#c62828', padding: '12px', borderRadius: '4px', marginBottom: '16px' },
  loading: { color: '#666', padding: '20px' },
};

const accent = (color: string): React.CSSProperties => ({ ...styles.card, borderLeft: `4px solid ${color}` });

const StatCard: React.FC<{ label: string; value: number; color?: string }> = ({ label, value, color = '#1a73e8' }) => (
  <div style={accent(color)}>
    <div style={styles.cardValue}>{value}</div>
    <div style={styles.cardLabel}>{label}</div>
  </div>
);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const res = await client.get<DashboardStats>('/dashboard/stats');
      setStats(res.data);
      setError('');
    } catch {
      setError('Failed to load dashboard stats.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (loading) return <div style={styles.loading}>Loading dashboard…</div>;

  return (
    <div>
      <h2 style={styles.heading}>Dashboard</h2>
      {error && <div style={styles.error}>{error}</div>}
      <p style={styles.refreshNote}>Auto-refreshes every 30 seconds</p>

      <div style={styles.sectionLabel}>Student Overview</div>
      <div style={styles.grid}>
        <StatCard label="Total Students" value={stats?.total_students ?? 0} color="#1a73e8" />
        <StatCard label="Validated" value={stats?.validated ?? 0} color="#34a853" />
        <StatCard label="Pending Review" value={stats?.pending_review ?? 0} color="#ea4335" />
        <StatCard label="Bulk Uploaded" value={stats?.bulk_uploaded ?? 0} color="#fbbc04" />
        <StatCard label="Student Registered" value={stats?.student_registered ?? 0} color="#4285f4" />
      </div>

      <div style={styles.sectionLabel}>Discrepancy Overview</div>
      <div style={styles.grid}>
        <StatCard label="Total Discrepancies" value={stats?.total_discrepancies ?? 0} color="#9c27b0" />
        <StatCard label="Critical" value={stats?.critical ?? 0} color="#ea4335" />
        <StatCard label="High" value={stats?.high ?? 0} color="#ff6d00" />
        <StatCard label="Resolved" value={stats?.resolved ?? 0} color="#34a853" />
      </div>

      <div style={styles.sectionLabel}>Students per Department</div>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Department</th>
            <th style={styles.th}>Students</th>
          </tr>
        </thead>
        <tbody>
          {stats?.students_per_department?.length ? (
            stats.students_per_department.map((row) => (
              <tr key={row.department}>
                <td style={styles.td}>{row.department}</td>
                <td style={styles.td}>{row.count}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td style={styles.td} colSpan={2}>No data available</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;

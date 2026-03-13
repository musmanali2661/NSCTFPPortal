import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

const styles: Record<string, React.CSSProperties> = {
  wrapper: { display: 'flex', height: '100vh', fontFamily: 'Segoe UI, sans-serif' },
  sidebar: {
    width: '220px',
    background: '#1e3a5f',
    color: '#fff',
    display: 'flex',
    flexDirection: 'column',
    flexShrink: 0,
  },
  sidebarTitle: {
    padding: '20px 16px',
    fontSize: '13px',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '1px',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
    color: '#a8c4e0',
  },
  nav: { flex: 1, padding: '8px 0' },
  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  header: {
    background: '#1a73e8',
    color: '#fff',
    padding: '0 24px',
    height: '56px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexShrink: 0,
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
  },
  headerTitle: { fontSize: '18px', fontWeight: 600 },
  logoutBtn: {
    background: 'rgba(255,255,255,0.2)',
    color: '#fff',
    border: '1px solid rgba(255,255,255,0.4)',
    padding: '6px 14px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  content: { flex: 1, overflow: 'auto', padding: '24px', background: '#f0f4f8' },
};

const navLinkStyle = ({ isActive }: { isActive: boolean }): React.CSSProperties => ({
  display: 'block',
  padding: '10px 20px',
  color: isActive ? '#fff' : '#a8c4e0',
  textDecoration: 'none',
  background: isActive ? 'rgba(26,115,232,0.4)' : 'transparent',
  borderLeft: isActive ? '3px solid #1a73e8' : '3px solid transparent',
  fontSize: '14px',
  transition: 'all 0.15s',
});

interface Props {
  children: React.ReactNode;
}

const NAV_LINKS = [
  { to: '/dashboard', label: '📊 Dashboard' },
  { to: '/students', label: '🎓 Students' },
  { to: '/discrepancies', label: '⚠️ Discrepancies' },
  { to: '/upload', label: '📤 Upload Data' },
  { to: '/tickets', label: '🎫 Tickets' },
  { to: '/question-bank', label: '📝 Question Bank' },
];

const Layout: React.FC<Props> = ({ children }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div style={styles.wrapper}>
      <aside style={styles.sidebar}>
        <div style={styles.sidebarTitle}>NSCT Portal</div>
        <nav style={styles.nav}>
          {NAV_LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} style={navLinkStyle}>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div style={styles.main}>
        <header style={styles.header}>
          <span style={styles.headerTitle}>NSCT Focal Person Portal</span>
          <button style={styles.logoutBtn} onClick={handleLogout}>
            Logout
          </button>
        </header>
        <main style={styles.content}>{children}</main>
      </div>
    </div>
  );
};

export default Layout;

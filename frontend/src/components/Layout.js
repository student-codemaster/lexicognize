import React, { useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import {
  Container,
  Navbar,
  Nav,
  Dropdown,
  Badge,
  Offcanvas,
  Button
} from 'react-bootstrap';
import {
  PersonCircle,
  BoxArrowRight,
  GearFill,
  BellFill,
  List,
  HouseFill,
  Upload,
  Cpu,
  GraphUp,
  Magic,
  FilePdf,
  Translate,
  Globe,
  Database,
  PeopleFill,
  ShieldLock
} from 'react-bootstrap-icons';
import { useAuth } from '../auth/AuthContext';

function Layout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showSidebar, setShowSidebar] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleSidebar = () => setShowSidebar(!showSidebar);

  const navigationItems = [
    { path: '/dashboard', icon: <HouseFill />, label: 'Dashboard' },
    { path: '/upload', icon: <Upload />, label: 'Datasets' },
    { path: '/train', icon: <Cpu />, label: 'Training' },
    { path: '/evaluate', icon: <GraphUp />, label: 'Evaluation' },
    { path: '/inference', icon: <Magic />, label: 'Inference' },
    { path: '/pdf-processor', icon: <FilePdf />, label: 'PDF Processing' },
    { path: '/language-tools', icon: <Translate />, label: 'Language Tools' },
    { path: '/translation', icon: <Globe />, label: 'Translation' },
  ];

  const adminItems = user?.role === 'admin' ? [
    { path: '/admin/users', icon: <PeopleFill />, label: 'User Management' },
    { path: '/admin/system', icon: <ShieldLock />, label: 'System Settings' },
  ] : [];

  return (
    <>
      {/* Navbar */}
      <Navbar bg="dark" variant="dark" expand="lg" className="shadow">
        <Container fluid>
          <Button
            variant="dark"
            className="me-2 d-lg-none"
            onClick={toggleSidebar}
          >
            <List />
          </Button>
          
          <Navbar.Brand as={Link} to="/dashboard" className="fw-bold">
            <Database className="me-2" />
            Legal Model Finetuner
          </Navbar.Brand>
          
          <Nav className="ms-auto d-none d-lg-flex">
            <Nav.Link as={Link} to="/profile">
              <PersonCircle className="me-1" />
              {user?.username}
              {user?.role && (
                <Badge bg="info" className="ms-2">
                  {user.role}
                </Badge>
              )}
            </Nav.Link>
            
            <Dropdown align="end">
              <Dropdown.Toggle variant="dark" id="dropdown-user">
                <GearFill />
              </Dropdown.Toggle>
              
              <Dropdown.Menu>
                <Dropdown.Item as={Link} to="/profile">
                  <PersonCircle className="me-2" />
                  Profile
                </Dropdown.Item>
                <Dropdown.Item as={Link} to="/settings">
                  <GearFill className="me-2" />
                  Settings
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item onClick={handleLogout}>
                  <BoxArrowRight className="me-2" />
                  Logout
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Nav>
          
          {/* Mobile user menu */}
          <Dropdown className="d-lg-none">
            <Dropdown.Toggle variant="dark" id="dropdown-mobile-user">
              <PersonCircle />
            </Dropdown.Toggle>
            
            <Dropdown.Menu>
              <Dropdown.Item as={Link} to="/profile">
                <PersonCircle className="me-2" />
                {user?.username}
              </Dropdown.Item>
              <Dropdown.Item as={Link} to="/settings">
                <GearFill className="me-2" />
                Settings
              </Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item onClick={handleLogout}>
                <BoxArrowRight className="me-2" />
                Logout
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Container>
      </Navbar>

      {/* Sidebar for mobile */}
      <Offcanvas show={showSidebar} onHide={toggleSidebar} responsive="lg">
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>
            <Database className="me-2" />
            Navigation
          </Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          <Nav className="flex-column">
            {navigationItems.map((item) => (
              <Nav.Link
                key={item.path}
                as={Link}
                to={item.path}
                onClick={() => setShowSidebar(false)}
                className="mb-2"
              >
                {item.icon}
                <span className="ms-2">{item.label}</span>
              </Nav.Link>
            ))}
            
            {adminItems.length > 0 && (
              <>
                <hr />
                <h6 className="text-muted mt-3 mb-2">Administration</h6>
                {adminItems.map((item) => (
                  <Nav.Link
                    key={item.path}
                    as={Link}
                    to={item.path}
                    onClick={() => setShowSidebar(false)}
                    className="mb-2"
                  >
                    {item.icon}
                    <span className="ms-2">{item.label}</span>
                  </Nav.Link>
                ))}
              </>
            )}
          </Nav>
        </Offcanvas.Body>
      </Offcanvas>

      {/* Main content */}
      <Container fluid className="mt-3">
        <div className="row">
          {/* Sidebar for desktop */}
          <div className="col-lg-2 d-none d-lg-block">
            <div className="card border-0 shadow-sm sticky-top" style={{ top: '80px' }}>
              <div className="card-body">
                <Nav className="flex-column">
                  {navigationItems.map((item) => (
                    <Nav.Link
                      key={item.path}
                      as={Link}
                      to={item.path}
                      className="mb-2 rounded"
                    >
                      {item.icon}
                      <span className="ms-2">{item.label}</span>
                    </Nav.Link>
                  ))}
                  
                  {adminItems.length > 0 && (
                    <>
                      <hr className="my-3" />
                      <h6 className="text-muted mb-2">Administration</h6>
                      {adminItems.map((item) => (
                        <Nav.Link
                          key={item.path}
                          as={Link}
                          to={item.path}
                          className="mb-2 rounded"
                        >
                          {item.icon}
                          <span className="ms-2">{item.label}</span>
                        </Nav.Link>
                      ))}
                    </>
                  )}
                </Nav>
              </div>
            </div>
          </div>
          
          {/* Main content area */}
          <div className="col-lg-10">
            <Outlet />
          </div>
        </div>
      </Container>
    </>
  );
}

export default Layout;
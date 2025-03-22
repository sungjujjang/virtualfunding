import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Navbar, Nav, Button } from 'react-bootstrap';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './index.css';
import Navbars from './components/navbar';
import LoginPage from './components/login';
import RegiPage from './components/register';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <Router>
    <Navbars />
    <Routes>
      <Route path="/" element='home' />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegiPage />} />
      <Route path="/contact" element='Contact' />
      <Route path="*" element='404' />
    </Routes>
  </Router>
);

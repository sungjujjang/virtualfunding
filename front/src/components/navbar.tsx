import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Button, Dropdown } from 'react-bootstrap';
import { Link } from 'react-router-dom';

async function GetUser(jwt: string) {
  return fetch(`http://localhost:1010/api/v1/get_user`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            jwt: jwt
        })
    })
    .then(res => res.json())
    .then(data => {
      return data;
    });
}

function Logout() {
    localStorage.removeItem('AccessToken');
    window.location.href = '/';
}

const Navbars: React.FC = () => {
  const [user, setUser] = useState<string | null>(null);  // 유저 상태

  useEffect(() => {
    const AccessToken = localStorage.getItem('AccessToken');
    console.log(AccessToken);
    if (AccessToken) {
      GetUser(AccessToken).then(data => {
        if (data && data.user && data.user.length > 0) {
          setUser(data.user[0]);
        } else {
          setUser(null);
        }
      });
    }
  }, []);

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/">
            <img
                src="/logo192.png"
                width="30"
                height="30"
                className="d-inline-block align-top"
                alt="React Bootstrap logo"
            />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link as={Link} to="/">홈</Nav.Link>
            <Nav.Link as={Link} to="/about">소개</Nav.Link>
            <Nav.Link as={Link} to="/contact">연락처</Nav.Link>
            <p>ㅤ</p>
            {/* 로그인한 유저가 있을 경우 */}
            {user ? (
              <Dropdown align="end">
                <Dropdown.Toggle variant="outline-light" id="dropdown-custom-components">
                  {user} <i className="bi bi-person-circle"></i>  {/* 유저 닉네임 표시 */}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item as={Link} to="/mypage">마이페이지</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/holdings">보유현황</Dropdown.Item>
                  <Dropdown.Item onClick={Logout}>로그아웃</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            ) : (
              // 로그인하지 않았다면 로그인 버튼 표시
              <Nav.Item>
                <Link to="/login">
                  <Button variant="outline-light" style={{ textDecoration: 'none' }}>
                    로그인
                  </Button>
                </Link>
              </Nav.Item>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navbars;

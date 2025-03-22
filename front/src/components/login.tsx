import React, { useState } from 'react';
import { Form, Button, Container } from 'react-bootstrap';
import './login.css'; // 애니메이션을 위한 CSS 파일
import { Link } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const [id, setid] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 폼 제출 처리 (로그인 또는 회원가입)
    if (!id || !password) {
      alert('아이디와 비밀번호를 입력하세요.');
      return;
    }
    console.log({ id, password });
    fetch('http://localhost:1010/api/v1/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id,
            password
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data && data.jwt) {
            localStorage.setItem('AccessToken', data.jwt);
            alert('로그인에 성공하셨습니다!');
            localStorage.setItem('UserId', id);
            window.location.href = '/';
        } else {
            alert('아이디 또는 비밀번호가 틀렸습니다.');
        }
    }
    );
  };

  return (
    <Container>
        <Form onSubmit={handleSubmit}>
            <h2>로그인</h2>
            <Form.Group controlId="id">
            <Form.Label>ID</Form.Label>
            <Form.Control
                type="text"
                placeholder="유저 아이디를 입력하세요"
                value={id}
                onChange={(e) => setid(e.target.value)}
            />
            </Form.Group>
            <Form.Group controlId="password">
            <Form.Label>PASSWORD</Form.Label>
            <Form.Control
                type="password"
                placeholder="비밀번호를 입력하세요"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            </Form.Group>
            <Button variant="primary" type="submit">Login</Button>
            <Link to="/register">회원가입</Link>
        </Form>
    </Container>
  );
};

export default LoginPage;
import React, { JSX, useEffect, useState } from 'react';
import { Form, Button, Container } from 'react-bootstrap';
import './login.css'; // 애니메이션을 위한 CSS 파일
import { Link } from 'react-router-dom';

const RegiPage: React.FC = () => {
  const [id, setid] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [goodPassword, setGoodPassword] = useState<boolean>(false);
  const [isPasswordruleVisible, setIsPasswordruleVisible] = useState<boolean>(false);
  const [PasswordRule, setPasswordRule] = useState<JSX.Element | null>(null);

  useEffect(() => {
    setPasswordRule(
        <ul>
            <li>8자 이상</li>
            <li>숫자 포함</li>
        </ul>
    );
  }, []);

  function checkPassword() {
    const rules = [];
    if (password.length < 8) {
        rules.push(<li key="length">8자 이상</li>);
    }
    if (!password.match(/[0-9]/g)) {
        rules.push(<li key="number">숫자 포함</li>);
    }
    if (rules.length === 0) {
        setIsPasswordruleVisible(false);
        setGoodPassword(true);
    } else {
        setPasswordRule(<ul>{rules}</ul>);
    }
  }
    


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 폼 제출 처리 (로그인 또는 회원가입)
    if (!id || !password || !name || !email) {
      alert('모든 칸을 채워 주세요.');
      return;
    }
    if (!goodPassword) {
        alert('비밀번호가 조건에 맞지 않습니다.');
        return;
    }
    console.log({ id, password });
    fetch('http://localhost:1010/api/v1/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id,
            password,
            name,
            email
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data && data.jwt) {
            localStorage.setItem('AccessToken', data.jwt);
            alert('회원가입에 성공하셨습니다!');
            localStorage.setItem('UserId', id);
            window.location.href = '/';
        } else {
            alert('이미 있는 아이디 입니다.');
        }
    }
    );
  };

  return (
    <Container>
        <Form onSubmit={handleSubmit}>
            <h2>회원가입</h2>
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
                    onChange={(e) => {
                        setPassword(e.target.value)
                        checkPassword();
                    }}
                    onFocus={() => setIsPasswordruleVisible(true)}
                    onBlur={() => setIsPasswordruleVisible(false)}
                />
                {isPasswordruleVisible && (
                    <div className="password-rule"><br />
                        {PasswordRule}
                    </div>
                )}
            </Form.Group>
            <Form.Group controlId="name">
                <Form.Label>NAME</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="이름을 입력하세요"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
            </Form.Group>
            <Form.Group controlId="email">
                <Form.Label>EMAIL</Form.Label>
                <Form.Control
                    type="email"
                    placeholder="이메일을 입력하세요"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </Form.Group>
            <Button variant="primary" type="submit">Register</Button>
            <Link to="/login">로그인</Link>
        </Form>
    </Container>
  );
};

export default RegiPage;
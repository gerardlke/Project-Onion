import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck, faInfoCircle, faTimes } from '@fortawesome/free-solid-svg-icons';
import './Login.css';


const USER_REGEX = /^[A-Za-z][A-Za-z0-9-_]{3,23}$/;
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;

const Register = () => {
    const navigate = useNavigate();
    const userRef = useRef();
    const errRef = useRef();
    
    const [user, setUser] = useState('');
    const [validName, setValidName] = useState(false);
    const [userFocus, setUserFocus] = useState(false);

    const [pwd, setPwd] = useState('');
    const [validPwd, setValidPwd] = useState(false);
    const [pwdFocus, setPwdFocus] = useState(false);

    const [matchPwd, setMatchPwd] = useState('');
    const [validMatch, setValidMatch] = useState(false);
    const [matchFocus, setMatchFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        userRef.current?.focus();
    }, []);

    // check if username is valid
    useEffect(() => {
        const result = USER_REGEX.test(user);
        setValidName(result);
    }, [user]);
    
    // check if password is valid
    useEffect(() => {
        const result = PWD_REGEX.test(pwd);
        setValidPwd(result);
    }, [pwd]);

    // check if password and confirm password match
    useEffect(() => {
        const result = matchPwd === pwd;
        setValidMatch(result);
    }, [matchPwd, pwd]);

    //error message
    useEffect(() => {
        setErrMsg('');
    }, [user, pwd, matchPwd]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validName || !validPwd || !validMatch) {
            setErrMsg('Please fix the highlighted fields before signing up.');
            return;
        }

        setIsSubmitting(true);

        try {
            const response = await fetch('/user/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: user, password: pwd }),
            });

            if (!response.ok) {
                const errorBody = await response.json().catch(() => null);
                setErrMsg(errorBody?.detail || 'Registration failed. Please try again.');
                return;
            }

            navigate('/login');
        } catch (error) {
            setErrMsg('Registration service is unavailable. Please try again later.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
    <div className="auth-page">
        <p ref={errRef} className={errMsg ? 'auth-error' : 'offscreen'} aria-live="assertive">
        {errMsg}
        </p>
        <p className="auth-wordmark">Project Onion</p>
        <div className="auth-card">
        <div className="auth-card-header">
            <p className="auth-card-eyebrow">Get started</p>
            <h2 className="auth-card-title">Create account</h2>
        </div>

        <form onSubmit={handleSubmit}>
            {/* Username */}
            <div className="auth-field">
            <label className="auth-label" htmlFor="register-username">
                Username
                <span className={validName ? 'auth-valid' : 'hide'}>
                <FontAwesomeIcon icon={faCheck} />
                </span>
                <span className={validName || !user ? 'hide' : 'auth-invalid'}>
                <FontAwesomeIcon icon={faTimes} />
                </span>
            </label>
            <input
                id="register-username"
                className="auth-input"
                type="text"
                ref={userRef}
                autoComplete="off"
                onChange={(e) => setUser(e.target.value)}
                required
                aria-invalid={validName ? 'false' : 'true'}
                aria-describedby="uidnote"
                onFocus={() => setUserFocus(true)}
                onBlur={() => setUserFocus(false)}
            />
            {userFocus && user && !validName && (
                <p id="uidnote" className="auth-hint">
                <FontAwesomeIcon icon={faInfoCircle} /> 4–24 characters. Must begin with a letter. Letters, numbers, _ and - allowed.
                </p>
            )}
            </div>

            {/* Password */}
            <div className="auth-field">
            <label className="auth-label" htmlFor="register-password">
                Password
                <span className={validPwd ? 'auth-valid' : 'hide'}>
                <FontAwesomeIcon icon={faCheck} />
                </span>
                <span className={validPwd || !pwd ? 'hide' : 'auth-invalid'}>
                <FontAwesomeIcon icon={faTimes} />
                </span>
            </label>
            <input
                id="register-password"
                className="auth-input"
                type="password"
                onChange={(e) => setPwd(e.target.value)}
                required
                aria-invalid={validPwd ? 'false' : 'true'}
                aria-describedby="pwdnote"
                onFocus={() => setPwdFocus(true)}
                onBlur={() => setPwdFocus(false)}
                placeholder="••••••••"
            />
            {pwdFocus && pwd && !validPwd && (
                <p id="pwdnote" className="auth-hint">
                <FontAwesomeIcon icon={faInfoCircle} /> 8–24 characters. Uppercase, lowercase, number and one of: ! @ # $ %
                </p>
            )}
            </div>

            {/* Confirm password */}
            <div className="auth-field">
            <label className="auth-label" htmlFor="confirm_pwd">
                Confirm password
                <span className={validMatch && matchPwd ? 'auth-valid' : 'hide'}>
                <FontAwesomeIcon icon={faCheck} />
                </span>
                <span className={validMatch || !matchPwd ? 'hide' : 'auth-invalid'}>
                <FontAwesomeIcon icon={faTimes} />
                </span>
            </label>
            <input
                id="confirm_pwd"
                className="auth-input"
                type="password"
                onChange={(e) => setMatchPwd(e.target.value)}
                required
                aria-invalid={validMatch ? 'false' : 'true'}
                aria-describedby="confirmnote"
                onFocus={() => setMatchFocus(true)}
                onBlur={() => setMatchFocus(false)}
                placeholder="••••••••"
            />
            {matchFocus && matchPwd && !validMatch && (
                <p id="confirmnote" className="auth-hint">
                <FontAwesomeIcon icon={faInfoCircle} /> Must match the password above.
                </p>
            )}
            </div>

            <button
            className="auth-btn"
            disabled={!validName || !validPwd || !validMatch || isSubmitting}
            >
            {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
        </form>

        <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
        </p>
        </div>
    </div>
    );

}

export default Register;

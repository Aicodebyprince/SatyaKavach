import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import Icon from '../components/Icon';
import Logo from '../components/Logo';
import { authAPI } from '../services/api';

export default function RegisterPage() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError(lang === 'hi' ? 'पासवर्ड मेल नहीं खाते' : 'Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError(lang === 'hi' ? 'पासवर्ड कम से कम 6 अक्षरों का हो' : 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await authAPI.register({ email, password, full_name: fullName });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-[75vh] items-center justify-center px-4 py-16">
      <div className="absolute left-1/2 top-1/2 h-[380px] w-[380px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-500/[0.06] blur-[100px]" />

      <div className="gradient-border animate-fade-up w-full max-w-md rounded-2xl shadow-glow-lg">
        <div className="space-y-6 rounded-2xl p-8 sm:p-10">
          <div className="text-center">
            <Logo className="mx-auto h-12 w-12" id="registerLogoGrad" />
            <h1 className="font-display mt-4 text-2xl font-bold text-white">{t('register', lang)}</h1>
            <p className="mt-1 text-sm text-slate-500">
              {lang === 'hi' ? 'नया खाता बनाएं — मुफ़्त में जाँच शुरू करें' : 'Create an account — start verifying for free'}
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-2.5 rounded-xl border border-red-400/25 bg-red-500/[0.07] p-3.5">
              <Icon name="alertCircle" className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <Field
              label={t('fullName', lang)}
              icon="user"
              input={
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="input-field !pl-10"
                  placeholder={lang === 'hi' ? 'आपका नाम' : 'Your name'}
                />
              }
            />
            <Field
              label={t('emailOrPhone', lang)}
              icon="mail"
              input={
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field !pl-10"
                  placeholder={lang === 'hi' ? 'ईमेल' : 'email@example.com'}
                  required
                />
              }
            />
            <Field
              label={t('password', lang)}
              icon="lock"
              input={
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field !pl-10"
                  placeholder="••••••••"
                  required
                />
              }
            />
            <Field
              label={t('confirmPassword', lang)}
              icon="shieldCheck"
              input={
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-field !pl-10"
                  placeholder="••••••••"
                  required
                />
              }
            />

            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">
              {loading ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent" />
              ) : (
                <>
                  {t('register', lang)}
                  <Icon name="arrowRight" className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500">
            {t('hasAccount', lang)}{' '}
            <Link to="/login" className="font-semibold text-saffron-400 hover:underline">
              {t('login', lang)}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  icon,
  input,
}: {
  label: string;
  icon: Parameters<typeof Icon>[0]['name'];
  input: React.ReactNode;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <div className="relative">
        <Icon name={icon} className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        {input}
      </div>
    </div>
  );
}

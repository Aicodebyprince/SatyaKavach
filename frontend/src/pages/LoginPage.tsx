import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import Icon from '../components/Icon';
import Logo from '../components/Logo';
import { authAPI } from '../services/api';

export default function LoginPage() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authAPI.login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAnonymous = async () => {
    try {
      await authAPI.anonymous();
      navigate('/');
    } catch {
      setError('Anonymous session failed');
    }
  };

  return (
    <div className="relative flex min-h-[75vh] items-center justify-center px-4 py-16">
      <div className="absolute left-1/2 top-1/2 h-[380px] w-[380px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-saffron-500/[0.06] blur-[100px]" />

      <div className="gradient-border animate-fade-up w-full max-w-md rounded-2xl shadow-glow-lg">
        <div className="space-y-6 rounded-2xl p-8 sm:p-10">
          {/* Brand */}
          <div className="text-center">
            <Logo className="mx-auto h-12 w-12" id="loginLogoGrad" />
            <h1 className="font-display mt-4 text-2xl font-bold text-white">{t('login', lang)}</h1>
            <p className="mt-1 text-sm text-slate-500">
              {lang === 'hi' ? 'सत्यकवच में आपका स्वागत है' : 'Welcome back to SatyaKavach'}
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-2.5 rounded-xl border border-red-400/25 bg-red-500/[0.07] p-3.5">
              <Icon name="alertCircle" className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <FormField
              label={t('emailOrPhone', lang)}
              icon="mail"
              input={
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field !pl-10"
                  placeholder={lang === 'hi' ? 'ईमेल या फ़ोन' : 'email or phone'}
                  required
                />
              }
            />
            <FormField
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

            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">
              {loading ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent" />
              ) : (
                <>
                  {t('login', lang)}
                  <Icon name="arrowRight" className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="space-y-3 text-center">
            <p className="text-sm text-slate-500">
              {t('noAccount', lang)}{' '}
              <Link to="/register" className="font-semibold text-saffron-400 hover:underline">
                {t('register', lang)}
              </Link>
            </p>

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-white/[0.07]" />
              <span className="text-2xs font-semibold uppercase tracking-widest text-slate-600">{t('or', lang)}</span>
              <div className="h-px flex-1 bg-white/[0.07]" />
            </div>

            <button onClick={handleAnonymous} className="btn-outline w-full">
              <Icon name="user" className="h-4 w-4 text-slate-400" />
              {t('anonymousVerify', lang)}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function FormField({
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

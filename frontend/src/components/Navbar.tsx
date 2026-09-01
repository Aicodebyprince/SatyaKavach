import { Link, useLocation } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import Logo from './Logo';
import Icon from './Icon';

export default function Navbar() {
  const { lang, setLang } = useLang();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 border-b border-white/[0.06] bg-ink-950/70 backdrop-blur-xl">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Brand */}
          <Link to="/" className="group flex items-center gap-3">
            <div className="transition-transform duration-300 group-hover:scale-110">
              <Logo className="h-9 w-9" />
            </div>
            <div className="hidden sm:block">
              <p className="font-display text-[15px] font-bold leading-tight text-white">
                Satya<span className="text-gradient">Kavach</span>
              </p>
              <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-500">
                {lang === 'hi' ? 'सत्य के लिए कवच' : 'Armor for the Truth'}
              </p>
            </div>
          </Link>

          {/* Center links */}
          <div className="flex items-center gap-1.5">
            <NavLink to="/" active={isActive('/')} icon="shieldCheck" label={t('home', lang)} />
            <NavLink
              to="/history"
              active={isActive('/history')}
              icon="history"
              label={t('history', lang)}
              hideLabelOnMobile
            />

            <div className="mx-1 hidden h-6 w-px bg-white/10 sm:block" />

            {/* Language toggle */}
            <button
              onClick={() => setLang(lang === 'hi' ? 'en' : 'hi')}
              className="group flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-semibold text-slate-300 transition-all duration-200 hover:border-saffron-500/40 hover:text-white"
              aria-label="Toggle language"
            >
              <Icon name="globe" className="h-3.5 w-3.5 text-saffron-400" />
              {lang === 'hi' ? 'हिंदी' : 'EN'}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavLink({
  to,
  active,
  icon,
  label,
  hideLabelOnMobile,
}: {
  to: string;
  active: boolean;
  icon: Parameters<typeof Icon>[0]['name'];
  label: string;
  hideLabelOnMobile?: boolean;
}) {
  return (
    <Link
      to={to}
      className={`relative flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-all duration-200 ${
        active
          ? 'bg-white/[0.07] text-saffron-400'
          : 'text-slate-400 hover:bg-white/[0.04] hover:text-white'
      }`}
    >
      <Icon name={icon} className="h-[18px] w-[18px]" />
      <span className={hideLabelOnMobile ? 'hidden lg:inline' : ''}>{label}</span>
      {active && (
        <span className="absolute -bottom-[13px] left-1/2 h-0.5 w-8 -translate-x-1/2 rounded-full bg-gradient-to-r from-saffron-500 to-amber-400" />
      )}
    </Link>
  );
}

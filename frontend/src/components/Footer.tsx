import { useLang } from '../App';
import { t } from '../i18n/translations';
import Logo from './Logo';
import Icon from './Icon';

export default function Footer() {
  const { lang } = useLang();

  return (
    <footer className="border-t border-white/[0.06] bg-ink-900/40 px-4 py-12">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-10 md:grid-cols-3">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3">
              <Logo className="h-8 w-8" id="footerLogoGrad" />
              <p className="font-display text-sm font-bold text-white">
                Satya<span className="text-gradient">Kavach</span>
              </p>
            </div>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-slate-500">{t('tagline', lang)}</p>
            <p className="mt-2 text-xs text-slate-600">
              {lang === 'hi'
                ? 'सत्य (Truth) + कवच (Armor) — AI से सच्चाई की रक्षा'
                : 'Satya (Truth) + Kavach (Armor) — protecting truth with AI'}
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              {lang === 'hi' ? 'उपयोगी लिंक' : 'Resources'}
            </h4>
            <ul className="mt-4 space-y-2.5 text-sm">
              <FooterLink href="/docs" icon="externalLink" label="API Docs" />
              <FooterLink href="https://github.com" icon="externalLink" label="GitHub" />
              <FooterLink href="https://i4c.gov.in" icon="flag" label="I4C / Cyber 1930" />
            </ul>
          </div>

          {/* Team */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{t('team', lang)}</h4>
            <ul className="mt-4 space-y-2 text-sm text-slate-400">
              <li>Prince Sherathiya</li>
              <li>Soham Shetye</li>
            </ul>
            <p className="mt-3 text-xs text-slate-600">{t('builtFor', lang)}</p>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-white/[0.06] pt-6 text-xs text-slate-600 sm:flex-row">
          <p>© 2026 SatyaKavach · MIT License</p>
          <p className="flex items-center gap-1.5">
            <Icon name="zap" className="h-3 w-3 text-saffron-500" />
            Omnikon National Hackathon 2026 · Problem PS4 — CyberTech
          </p>
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ href, icon, label }: { href: string; icon: Parameters<typeof Icon>[0]['name']; label: string }) {
  return (
    <li>
      <a
        href={href}
        className="group inline-flex items-center gap-2 text-slate-400 transition-colors duration-200 hover:text-saffron-400"
      >
        <Icon name={icon} className="h-3.5 w-3.5 text-slate-600 transition-colors group-hover:text-saffron-500" />
        {label}
      </a>
    </li>
  );
}

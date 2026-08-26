import { useState, useRef, useCallback } from 'react';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import Icon from './Icon';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onLinkSubmit: (url: string) => void;
  isLoading?: boolean;
}

const ACCEPTED_TYPES = '.jpg,.jpeg,.png,.webp,.mp4,.mov,.avi,.mp3,.wav,.m4a';

export default function FileUpload({ onFileSelect, onLinkSubmit, isLoading }: FileUploadProps) {
  const { lang } = useLang();
  const [isDragging, setIsDragging] = useState(false);
  const [linkInput, setLinkInput] = useState('');
  const [showLinkInput, setShowLinkInput] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect],
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  const handleLinkSubmit = () => {
    if (linkInput.trim()) {
      onLinkSubmit(linkInput.trim());
      setLinkInput('');
    }
  };

  return (
    <div className="w-full space-y-5">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && fileInputRef.current?.click()}
        className={`group relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed p-10 text-center
                    transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron-400/50
                    ${
                      isDragging
                        ? 'scale-[1.01] border-saffron-400/70 bg-saffron-500/[0.07] shadow-glow'
                        : 'border-white/10 bg-white/[0.02] hover:border-saffron-500/40 hover:bg-white/[0.04]'
                    }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Hover sheen */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-saffron-500/[0.04] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

        <div className="relative space-y-4">
          {/* Icon ring */}
          <div
            className={`mx-auto flex h-[72px] w-[72px] items-center justify-center rounded-2xl border transition-all duration-300 ${
              isDragging
                ? 'border-saffron-400/60 bg-saffron-500/20 shadow-glow'
                : 'border-white/10 bg-gradient-to-br from-saffron-500/15 to-violet-500/10 group-hover:border-saffron-500/40 group-hover:shadow-glow'
            }`}
          >
            <Icon
              name="uploadCloud"
              className={`h-8 w-8 transition-colors duration-300 ${
                isDragging ? 'text-saffron-300' : 'text-saffron-400'
              }`}
              strokeWidth={1.6}
            />
          </div>

          <div>
            <p className="font-display text-base font-semibold text-white">
              {isDragging ? (lang === 'hi' ? 'छोड़ें — जाँच शुरू!' : 'Drop it — we’ll check it!') : t('dragDrop', lang)}
            </p>
            <p className="mt-1.5 text-sm text-slate-500">
              {lang === 'hi' ? 'या क्लिक करके फ़ाइल चुनें · अधिकतम 50MB' : 'or click to browse · max 50MB'}
            </p>
          </div>

          {/* Format chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            <FormatChip icon="image" label="JPG · PNG · WebP" tone="sky" />
            <FormatChip icon="video" label="MP4 · MOV" tone="violet" />
            <FormatChip icon="mic" label="MP3 · WAV" tone="emerald" />
            <FormatChip icon="link" label="URL" tone="amber" />
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="flex items-center gap-4">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <span className="text-2xs font-semibold uppercase tracking-[0.2em] text-slate-600">{t('or', lang)}</span>
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </div>

      {/* Link input */}
      {!showLinkInput ? (
        <button
          onClick={() => setShowLinkInput(true)}
          className="btn-outline w-full !py-3"
          type="button"
        >
          <Icon name="link" className="h-4 w-4 text-saffron-400" />
          {t('pasteLink', lang)}
        </button>
      ) : (
        <div className="animate-fade-up space-y-2">
          <label className="label">{lang === 'hi' ? 'संदिग्ध लिंक' : 'Suspicious link'}</label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Icon name="link" className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input
                type="url"
                value={linkInput}
                onChange={(e) => setLinkInput(e.target.value)}
                placeholder="https://example.com/suspicious-link"
                className="input-field !pl-10"
                onKeyDown={(e) => e.key === 'Enter' && handleLinkSubmit()}
                autoFocus
              />
            </div>
            <button
              type="button"
              onClick={handleLinkSubmit}
              disabled={!linkInput.trim() || isLoading}
              className="btn-primary shrink-0"
            >
              <Icon name="zap" className="h-4 w-4" />
              {t('verify', lang)}
            </button>
          </div>
          <p className="text-xs text-slate-600">
            {lang === 'hi'
              ? 'थ्रेट इंटेलिजेंस स्रोतों (VirusTotal, Safe Browsing, PhishTank) से मिलान होगा'
              : 'Checked against threat intelligence sources (VirusTotal, Safe Browsing, PhishTank)'}
          </p>
        </div>
      )}
    </div>
  );
}

function FormatChip({
  icon,
  label,
  tone,
}: {
  icon: Parameters<typeof Icon>[0]['name'];
  label: string;
  tone: 'sky' | 'violet' | 'emerald' | 'amber';
}) {
  const tones = {
    sky: 'border-sky-400/20 bg-sky-400/[0.07] text-sky-300',
    violet: 'border-violet-400/20 bg-violet-400/[0.07] text-violet-300',
    emerald: 'border-emerald-400/20 bg-emerald-400/[0.07] text-emerald-300',
    amber: 'border-amber-400/20 bg-amber-400/[0.07] text-amber-300',
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-2xs font-medium ${tones[tone]}`}
    >
      <Icon name={icon} className="h-3 w-3" strokeWidth={2} />
      {label}
    </span>
  );
}

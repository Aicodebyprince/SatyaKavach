/**
 * SatyaKavach - i18n Translations (Hindi-First)
 */

export type Language = 'hi' | 'en';

export const translations = {
  hi: {
    // Navigation
    appName: '🛡️ सत्य कवच',
    tagline: 'सत्य की रक्षा कवच',
    home: 'होम',
    history: 'इतिहास',
    login: 'लॉगिन',
    register: 'रजिस्टर',

    // Home page
    heroTitle: 'मीडिया की सच्चाई जानें',
    heroSubtitle: 'AI से तस्वीरें, वीडियो और आवाज़ की जाँच करें — तुरंत विश्वास स्कोर पाएं',
    uploadImage: 'तस्वीर अपलोड करें',
    uploadVideo: 'वीडियो अपलोड करें',
    uploadAudio: 'आवाज़ अपलोड करें',
    pasteLink: 'लिंक पेस्ट करें',
    or: 'या',
    dragDrop: 'फ़ाइल यहाँ खींचें और छोड़ें',
    browse: 'फ़ाइल चुनें',
    supportedFormats: 'सहायक प्रारूप: JPG, PNG, WebP, MP4, MOV, MP3, WAV',

    // Results
    trustScore: 'विश्वास स्कोर',
    highTrust: 'विश्वसनीय',
    uncertain: 'अनिश्चित',
    lowTrust: 'अविश्वसनीय',
    evidenceReport: 'साक्ष्य रिपोर्ट',
    recommendedAction: 'सिफारिश',
    modelBreakdown: 'मॉडल विवरण',
    analysisComplete: 'जाँच पूरी!',
    analyzing: 'जाँच हो रही है...',
    preprocessing: 'मीडिया तैयार हो रहा है...',
    scoring: 'विश्वास स्कोर गणना हो रही है...',

    // Actions
    verify: 'जाँच करें',
    shareResult: 'परिणाम साझा करें',
    reportToI4C: 'I4C/1930 पर रिपोर्ट करें',
    uploadNew: 'नया मीडिया अपलोड करें',
    viewHistory: 'इतिहास देखें',

    // Error messages
    unsupportedFile: 'कृपया सही फ़ाइल प्रकार अपलोड करें: इमेज, वीडियो, या ऑडियो',
    fileTooLarge: 'फ़ाइल बहुत बड़ी है। कृपया छोटी फ़ाइल अपलोड करें।',
    analysisIncomplete: 'कुछ जाँच पूरी नहीं हो सकीं। परिणाम सीमित हो सकता है।',
    systemBusy: 'अभी बहुत व्यस्त हैं। कृपया कुछ क्षण बाद पुनः प्रयास करें।',

    // Auth
    emailOrPhone: 'ईमेल या फ़ोन नंबर',
    password: 'पासवर्ड',
    confirmPassword: 'पासवर्ड की पुष्टि करें',
    fullName: 'पूरा नाम',
    noAccount: 'खाता नहीं है?',
    hasAccount: 'पहले से खाता है?',
    anonymousVerify: 'बिना खाता जाँच करें',

    // Footer
    builtFor: 'ओम्निकॉन नेशनल हैकाथॉन 2026 के लिए बनाया गया',
    team: 'टीम कोडेटर्स',
  },

  en: {
    // Navigation
    appName: '🛡️ SatyaKavach',
    tagline: 'Armor for the Truth',
    home: 'Home',
    history: 'History',
    login: 'Login',
    register: 'Register',

    // Home page
    heroTitle: 'Verify Media Authenticity',
    heroSubtitle: 'AI-powered detection for images, videos, and audio — get an instant Trust Score',
    uploadImage: 'Upload Image',
    uploadVideo: 'Upload Video',
    uploadAudio: 'Upload Audio',
    pasteLink: 'Paste Link',
    or: 'or',
    dragDrop: 'Drag and drop a file here',
    browse: 'Choose File',
    supportedFormats: 'Supported: JPG, PNG, WebP, MP4, MOV, MP3, WAV',

    // Results
    trustScore: 'Trust Score',
    highTrust: 'Trustworthy',
    uncertain: 'Uncertain',
    lowTrust: 'Untrustworthy',
    evidenceReport: 'Evidence Report',
    recommendedAction: 'Recommended Action',
    modelBreakdown: 'Model Breakdown',
    analysisComplete: 'Analysis Complete!',
    analyzing: 'Analyzing...',
    preprocessing: 'Preparing media...',
    scoring: 'Computing trust score...',

    // Actions
    verify: 'Verify',
    shareResult: 'Share Result',
    reportToI4C: 'Report to I4C/1930',
    uploadNew: 'Upload New Media',
    viewHistory: 'View History',

    // Error messages
    unsupportedFile: 'Please upload a supported file type: image, video, or audio',
    fileTooLarge: 'The file is too large. Please upload a smaller file.',
    analysisIncomplete: 'Some checks could not be completed. The result may be limited.',
    systemBusy: 'We\'re experiencing high traffic. Please try again in a moment.',

    // Auth
    emailOrPhone: 'Email or Phone Number',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    fullName: 'Full Name',
    noAccount: 'Don\'t have an account?',
    hasAccount: 'Already have an account?',
    anonymousVerify: 'Verify without account',

    // Footer
    builtFor: 'Built for Omnikon National Hackathon 2026',
    team: 'Team Codeators',
  },
} as const;

export type TranslationKey = keyof typeof translations.hi;

export function t(key: TranslationKey, lang: Language = 'hi'): string {
  return translations[lang][key] || translations.hi[key] || key;
}

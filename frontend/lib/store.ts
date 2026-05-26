import { create } from 'zustand';

interface ResumeData {
  resume_id: string;
  candidate_name: string;
  email: string;
  phone?: string;
  location?: string;
  skills: string[];
  total_experience_years: number;
  current_title?: string;
  education_level?: string;
  summary?: string;
  [key: string]: any;
}

interface AppState {
  // Resume State
  resumeData: ResumeData | null;
  setResumeData: (data: ResumeData) => void;
  
  // Jobs State
  jobs: any[];
  setJobs: (jobs: any[]) => void;
  
  // Saved Jobs
  savedJobs: string[];
  addSavedJob: (jobId: string) => void;
  
  // UI State
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Theme
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useStore = create<AppState>((set) => ({
  // Resume
  resumeData: null,
  setResumeData: (data) => set({ resumeData: data }),
  
  // Jobs
  jobs: [],
  setJobs: (jobs) => set({ jobs }),
  
  // Saved
  savedJobs: [],
  addSavedJob: (jobId) => set((state) => ({
    savedJobs: [...state.savedJobs, jobId]
  })),
  
  // Loading
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
  
  // Theme
  theme: 'light',
  toggleTheme: () => set((state) => ({
    theme: state.theme === 'light' ? 'dark' : 'light'
  })),
}));

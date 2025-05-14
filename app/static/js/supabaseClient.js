const { createClient } = window.supabase;
const SUPABASE_URL = 'https://ajczeisisnyfhubsnjxh.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqY3plaXNpc255Zmh1YnNuanhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg2MDM1NjIsImV4cCI6MjA1NDE3OTU2Mn0.eLG_8rUH325xAIYxQA9IFNCdeqA84m7IdGcB5aZhSSU';

export const supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
      autoConfirmEmail: true,
      detectSessionInUrl: false,
      persistSession: true
    }
  });
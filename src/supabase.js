import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://icsfrszpcjlhqkgyyvsy.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imljc2Zyc3pwY2psaHFrZ3l5dnN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3MTE1MDQsImV4cCI6MjA4ODI4NzUwNH0.dr67tMTNfDJc6wfj2c6QJtk8RuFSC4DfJriSNZBOtck'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

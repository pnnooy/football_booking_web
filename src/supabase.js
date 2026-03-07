import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://icsfrszpcjlhqkgyyvsy.supabase.co'
const supabaseAnonKey = '***REMOVED***'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

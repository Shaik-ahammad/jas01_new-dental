"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// Assuming Card/Select are part of UI kit or using standard HTML for zero-dep compatibility
// Merged Icon set
import { 
  Upload, 
  FileBadge, 
  ShieldCheck, 
  Loader2, 
  AlertCircle, 
  Building2, 
  Clock, 
  ChevronDown 
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function DoctorSignup() {
  const router = useRouter();
  
  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [isCustomHospital, setIsCustomHospital] = useState(false);

  // Merged Form State
  const [formData, setFormData] = useState({
    // Identity (Version A)
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    
    // Professional Info (Merged A & B)
    hospital_name: "", // Used if custom
    hospital_select: "", // Used if selected from dropdown
    license_number: "", // Now explicit (Version B)
    specialization: "General Dentist",

    // AI Scheduling (Version B)
    scheduleMode: "continuous" as "continuous" | "interleaved",
    workMinutes: "",
    breakMinutes: ""
  });

  // Handle Text/Select Changes
  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle File Upload (Version A)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileName(e.target.files[0].name);
      // Note: In a real app, you would append this file to a FormData object
    }
  };

  // Toggle Hospital Input Mode
  const toggleHospitalMode = () => {
    setIsCustomHospital(!isCustomHospital);
    // Reset values to avoid confusion
    setFormData(prev => ({ ...prev, hospital_name: "", hospital_select: "" }));
  };

  // Submission Logic
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // 1. Validation Logic
    const finalHospital = isCustomHospital ? formData.hospital_name : formData.hospital_select;
    
    if (!finalHospital) {
      setError("Please select or enter a valid hospital name.");
      setLoading(false);
      return;
    }

    if (formData.scheduleMode === "interleaved" && (!formData.workMinutes || !formData.breakMinutes)) {
      setError("Please define both work and break durations for interleaved schedules.");
      setLoading(false);
      return;
    }

    try {
      // 2. Construct Payload (Merging A & B requirements)
      const payload = {
        email: formData.email,
        password: formData.password,
        full_name: `${formData.firstName} ${formData.lastName}`,
        role: "doctor",
        hospital_name: finalHospital,
        specialization: formData.specialization,
        license_number: formData.license_number,
        
        // New AI Configuration Data
        scheduling_config: {
          mode: formData.scheduleMode,
          work_duration: formData.workMinutes ? parseInt(formData.workMinutes) : null,
          break_duration: formData.breakMinutes ? parseInt(formData.breakMinutes) : null,
        },
        
        // Metadata about the file (Simulating file upload linkage)
        kyc_document_name: fileName || "pending_upload"
      };

      await api.post("/register", payload);

      // Success -> Redirect
      router.push("/auth/doctor/login");

    } catch (err: any) {
      console.error(err);
      if (err.response) {
        setError(err.response.data.detail || "Registration failed. Please check your details.");
      } else {
        setError("Network error. Server unavailable.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row">
        
        {/* LEFT SIDE: Branding & Trust (From Version A) */}
        <div className="bg-doctor p-8 md:w-1/3 text-white flex flex-col justify-between hidden md:flex">
          <div>
            <ShieldCheck className="h-12 w-12 mb-4" />
            <h3 className="text-xl font-bold">Partner with Al-Shifa</h3>
            <p className="mt-4 text-doctor-light text-sm">
              Join the most advanced dental AI network. We verify every practitioner to ensure patient trust.
            </p>
            
            <div className="mt-8 space-y-3">
              <div className="flex items-center gap-2 text-sm text-doctor-light">
                <Building2 className="h-4 w-4" /> <span>Hospital Integration</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-doctor-light">
                <Clock className="h-4 w-4" /> <span>Smart Scheduling</span>
              </div>
            </div>
          </div>
          <div className="text-xs text-doctor-light/70">
            © 2025 Al-Shifa Clinical
          </div>
        </div>

        {/* RIGHT SIDE: Hybrid Form */}
        <div className="p-8 md:w-2/3 overflow-y-auto max-h-[90vh]">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Doctor Registration</h2>
          <p className="text-sm text-slate-500 mb-6">Complete your profile to access the AI dashboard.</p>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-md flex items-center gap-2 border border-red-100">
              <AlertCircle className="h-4 w-4" /> {error}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleRegister}>
            
            {/* SECTION 1: Personal Identity */}
            <div className="space-y-3">
               <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Personal Details</h3>
               <div className="grid grid-cols-2 gap-4">
                  <Input 
                    label="First Name" 
                    name="firstName" 
                    onChange={handleChange} 
                    required 
                    placeholder="Dr. John"
                  />
                  <Input 
                    label="Last Name" 
                    name="lastName" 
                    onChange={handleChange} 
                    required 
                    placeholder="Doe"
                  />
               </div>
               <Input 
                 label="Professional Email" 
                 type="email" 
                 name="email" 
                 onChange={handleChange} 
                 required 
                 placeholder="dr.john@hospital.com"
               />
               <Input 
                 label="Password" 
                 type="password" 
                 name="password" 
                 onChange={handleChange} 
                 required 
               />
            </div>

            <hr className="border-slate-100" />

            {/* SECTION 2: Professional Verification (Merged A & B) */}
            <div className="space-y-3">
               <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Professional Credentials</h3>
               
               {/* Hospital Logic: Dropdown OR Text */}
               <div className="space-y-1">
                 <label className="text-sm font-medium text-slate-700">Hospital / Clinic</label>
                 
                 {!isCustomHospital ? (
                   <div className="relative">
                     <select 
                       name="hospital_select"
                       className="w-full p-2 border border-slate-300 rounded-md bg-white text-slate-900 focus:ring-2 focus:ring-doctor/50 focus:border-doctor outline-none appearance-none"
                       onChange={handleChange}
                       value={formData.hospital_select}
                     >
                       <option value="">Select verified hospital...</option>
                       <option value="Al-Shifa Dental Center">Al-Shifa Dental Center</option>
                       <option value="City Smile Hospital">City Smile Hospital</option>
                       <option value="Apex Dental Care">Apex Dental Care</option>
                     </select>
                     <ChevronDown className="absolute right-3 top-3 h-4 w-4 text-slate-400 pointer-events-none" />
                   </div>
                 ) : (
                    <Input 
                      name="hospital_name" 
                      placeholder="Enter exact hospital name" 
                      onChange={handleChange} 
                      value={formData.hospital_name}
                      autoFocus
                    />
                 )}
                 
                 <button 
                   type="button"
                   onClick={toggleHospitalMode}
                   className="text-xs text-doctor font-medium hover:underline flex items-center gap-1 mt-1"
                 >
                   {isCustomHospital ? "Back to list selection" : "Hospital not listed? Add manually"}
                 </button>
               </div>

               {/* License Input (Version B) */}
               <Input 
                 label="Medical License Number" 
                 name="license_number"
                 placeholder="e.g. PMC-12345-X"
                 onChange={handleChange} 
                 required 
               />

               {/* File Upload (Version A) */}
               <div className="space-y-2 pt-1">
                  <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                    <FileBadge className="h-4 w-4 text-doctor" /> 
                    Upload License (e-KYC)
                  </label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-4 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer relative group">
                    <input 
                      type="file" 
                      className="absolute inset-0 opacity-0 cursor-pointer" 
                      onChange={handleFileChange}
                      accept=".pdf,.jpg,.png"
                    />
                    <Upload className="h-6 w-6 text-slate-400 group-hover:text-doctor mb-1 transition-colors" />
                    <p className="text-sm text-slate-600 font-medium truncate max-w-[200px]">
                      {fileName ? fileName : "Click to upload License"}
                    </p>
                  </div>
               </div>
            </div>

            <hr className="border-slate-100" />

            {/* SECTION 3: AI Scheduling Config (Version B) */}
            <div className="space-y-3">
               <div className="flex items-center justify-between">
                 <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Scheduling Preferences</h3>
                 <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">New</span>
               </div>

               <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3">
                 <div className="space-y-1">
                   <label className="text-sm font-medium text-slate-700">Work Mode</label>
                   <div className="relative">
                      <select
                        name="scheduleMode"
                        className="w-full p-2 border border-slate-300 rounded-md bg-white text-sm"
                        value={formData.scheduleMode}
                        onChange={handleChange}
                      >
                        <option value="continuous">Continuous (Back-to-back patients)</option>
                        <option value="interleaved">Interleaved (Work + Scheduled Breaks)</option>
                      </select>
                   </div>
                 </div>

                 <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="text-xs text-slate-500">Work Duration (mins)</label>
                      <input 
                        type="number" 
                        name="workMinutes"
                        className="w-full p-2 border border-slate-300 rounded-md text-sm"
                        placeholder="e.g. 30"
                        onChange={handleChange}
                      />
                    </div>
                    
                    {formData.scheduleMode === "interleaved" && (
                      <div className="space-y-1 animate-in fade-in slide-in-from-left-2 duration-300">
                        <label className="text-xs text-slate-500">Break Duration (mins)</label>
                        <input 
                          type="number" 
                          name="breakMinutes"
                          className="w-full p-2 border border-slate-300 rounded-md text-sm"
                          placeholder="e.g. 5"
                          onChange={handleChange}
                        />
                      </div>
                    )}
                 </div>
               </div>
            </div>
            
            <Button variant="doctor" className="w-full mt-4" size="lg" disabled={loading}>
              {loading ? <Loader2 className="animate-spin h-5 w-5"/> : "Submit for Verification"}
            </Button>
          </form>
          
          <p className="mt-6 text-center text-xs text-slate-500">
            Already registered? <Link href="/auth/doctor/login" className="text-doctor font-bold underline">Login here</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
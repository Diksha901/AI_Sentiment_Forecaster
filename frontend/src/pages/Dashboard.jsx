import React,{useEffect,useState} from 'react';
import { useNavigate } from "react-router-dom";

import { motion } from 'framer-motion';
import { Search, Sparkles, TrendingUp, BarChart3, Globe2, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';


const Dashboard = () => {
    const navigate = useNavigate();
    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
            navigate("/login");
        }
    }, [navigate]);
const [query, setQuery] = useState("");
const [sentiment, setSentiment] = useState(null);
const [report, setReport] = useState("");
const handleAnalyze = async () => {

 const res = await fetch("http://localhost:8000/analyze-product",{
    method:"POST",
    headers:{
       "Content-Type":"application/json"
    },
    body: JSON.stringify({query})
 });

 const data = await res.json();

 setSentiment(data.sentiment);
 setReport(data.report);
}
    return (
        <DashboardLayout title="Insights Dashboard">
            {/* Search & Header */}
            <div className="space-y-8">
                <div>
                    <h1 className="text-4xl font-black text-white tracking-tight">Market Intelligence</h1>
                    <p className="text-slate-400 mt-2 text-lg">Real-time sentiment and trend analysis for your products.</p>
                </div>

                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                        <Search className="w-6 h-6 text-slate-500 group-focus-within:text-primary transition-colors" />
                    </div>

                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search for a product..."
                        className="w-full h-20 bg-white/[0.03] border border-white/10 rounded-[2rem] pl-16 pr-40 outline-none focus:border-primary/50 focus:bg-white/[0.05] transition-all text-xl shadow-2xl"
                    />
                    <button onClick={handleAnalyze} className="absolute right-3 top-3 bottom-3 px-10 bg-primary text-background-dark font-black rounded-2xl hover:brightness-110 active:scale-95 transition-all shadow-xl shadow-primary/20">
                        Analyze
                    </button>
                </div>
            </div>

            {/* Analytics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Sentiment Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="lg:col-span-2 bg-white/[0.03] border border-white/10 p-10 rounded-[3rem] shadow-2xl relative overflow-hidden"
                >
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 blur-[100px] rounded-full -mr-32 -mt-32"></div>
                    <div className="flex items-center justify-between mb-12 relative z-10">
                        <h3 className="text-2xl font-bold">Overall Sentiment</h3>
                        <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-2xl flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Last 30 Days</span>
                        </div>
                    </div>

                    <div className="flex flex-col md:flex-row items-center gap-16 relative z-10">
                        <div className="relative flex items-center justify-center p-4">
                            <svg className="w-48 h-48 transform -rotate-90">
                                <circle cx="96" cy="96" r="88" strokeWidth="16" stroke="currentColor" fill="transparent" className="text-white/5" />
                                <circle
                                    cx="96" cy="96" r="88" strokeWidth="16" stroke="currentColor" fill="transparent"
                                    strokeDasharray={552.92} strokeDashoffset={552.92 * (1 - ((sentiment?.positive ?? 0)/100))}
                                    className="text-primary transition-all duration-1000 ease-out"
                                    strokeLinecap="round"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-5xl font-black text-white">{sentiment?.positive ?? 0}%</span>
                                <span className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mt-1">Positive</span>
                            </div>
                        </div>

                        <div className="flex-1 w-full space-y-8">
                            {[
                                { label: 'Positive', value: sentiment?.positive, color: 'bg-primary' },
                                { label: 'Neutral', value: sentiment?.neutral, color: 'bg-slate-500' },
                                { label: 'Negative', value: sentiment?.negative, color: 'bg-red-500' }
                            ].map((item) => (
                                <div key={item.label} className="space-y-3">
                                    <div className="flex items-center justify-between text-sm font-bold">
                                        <span className="text-slate-400">{item.label}</span>
                                        <span className="text-white">{item.value ?? 0}</span>
                                    </div>
                                    <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden p-[2px] border border-white/5">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width:  `${item.value ?? 0}%` }}
                                            transition={{ duration: 1.5, ease: "easeOut" }}
                                            className={`${item.color} h-full rounded-full shadow-[0_0_10px_rgba(13,204,242,0.3)]`}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>

                {/* AI Insight Card */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gradient-to-br from-primary to-blue-500 rounded-[3rem] p-10 text-background-dark flex flex-col justify-between shadow-2xl relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 w-full h-full bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                    <div className="relative z-10">
                        <div className="bg-background-dark/20 w-14 h-14 rounded-2xl flex items-center justify-center mb-8 backdrop-blur-md">
                            <Sparkles className="w-8 h-8 text-background-dark" />
                        </div>
                        <h3 className="text-3xl font-black leading-none mb-6">AI Insight Summary</h3>
                        <p className="text-lg font-bold leading-relaxed opacity-90 italic">
                            {report}
                        </p>
                    </div>
                    <button className="w-full bg-background-dark text-primary py-5 rounded-2xl font-black text-sm uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-xl relative z-10">
                        Generate Full Report
                    </button>
                </motion.div>
            </div>

            {/* Global Trends */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="bg-white/[0.03] border border-white/10 rounded-[3rem] overflow-hidden shadow-2xl"
            >
                <div className="p-10 border-b border-white/5 flex items-center justify-between">
                    <h3 className="text-2xl font-bold">Global Emerging Trends</h3>
                    <button className="text-primary flex items-center gap-2 font-bold group hover:underline">
                        View All Trends <ArrowUpRight className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </button>
                </div>
                <div className="divide-y divide-white/5">
                    {[
                        { name: "Sustainable Packaging", cat: "Retail", vol: "1.2M+", growth: 42, color: "text-emerald-400", status: "High Potential", icon: Globe2 },
                        { name: "Generative Search UI", cat: "SaaS", vol: "840K", growth: 128, color: "text-emerald-400", status: "Explosive", icon: Zap },
                        { name: "Hyper-Local Logistics", cat: "Transport", vol: "410K", growth: -12, color: "text-orange-400", status: "Saturating", icon: TrendingUp }
                    ].map((trend, i) => (
                        <div key={i} className="p-8 flex flex-wrap items-center justify-between gap-6 hover:bg-white/[0.02] transition-colors group">
                            <div className="flex items-center gap-6">
                                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-background-dark transition-all duration-500">
                                    <trend.icon className="w-7 h-7" />
                                </div>
                                <div>
                                    <h4 className="text-xl font-bold">{trend.name}</h4>
                                    <p className="text-slate-500 text-sm font-medium">{trend.cat}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-16">
                                <div className="text-center">
                                    <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-1">Volume</p>
                                    <p className="text-lg font-bold">{trend.vol}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-1">Growth</p>
                                    <p className={`text-lg font-bold ${trend.growth > 0 ? 'text-emerald-400' : 'text-orange-400'}`}>
                                        {trend.growth > 0 ? '+' : ''}{trend.growth}%
                                    </p>
                                </div>
                                <div className={`${trend.color.replace('text', 'bg')}/10 ${trend.color} px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${trend.color.replace('text', 'border')}/20`}>
                                    {trend.status}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </motion.div>
        </DashboardLayout>
    );
};

export default Dashboard;

import React from 'react';
import { motion } from 'framer-motion';
import { Download, Plus, ChevronRight, TrendingUp, TrendingDown, Clock, Globe, Laptop, Zap, ArrowUpRight } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const MarketTrends = () => {
    const stats = [
        { label: 'Total Search Volume', value: '12.4M', trend: 14, icon: Globe },
        { label: 'Consumer Sentiment', value: '84%', trend: 2.1, icon: Zap },
        { label: 'Avg. CPC', value: '$1.28', trend: -4.5, icon: TrendingDown },
        { label: 'Conversion Potential', value: 'High', status: 'Peak', icon: TrendingUp },
    ];

    const products = [
        { rank: '01', name: 'Wireless Audio Pro', cat: 'Electronics', growth: 42, val: 85 },
        { rank: '02', name: 'Smart Home Hub V2', cat: 'IoT', growth: 28, val: 60 },
        { rank: '03', name: 'Active Wear Gen-Z', cat: 'Fashion', growth: 12, val: 30 },
    ];

    return (
        <DashboardLayout title="Market Trends Analysis">
            {/* Breadcrumbs & Header */}
            <div className="space-y-8">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                    <span>Dashboard</span>
                    <ChevronRight className="w-4 h-4" />
                    <span className="text-white font-bold">Market Trends Analysis</span>
                </div>

                <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <div className="max-w-3xl">
                        <h1 className="text-4xl font-black text-white tracking-tight mb-3">Market Trends Analysis</h1>
                        <p className="text-slate-400 text-lg leading-relaxed">
                            Real-time visualization of global product performance and consumer interest shifts across primary markets.
                        </p>
                    </div>
                    <div className="flex gap-4">
                        <button className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-bold hover:bg-white/10 transition-all">
                            <Download className="w-4 h-4" /> Export Data
                        </button>
                        <button className="flex items-center gap-2 px-6 py-3 bg-primary text-background-dark rounded-xl text-sm font-black shadow-lg shadow-primary/20">
                            <Plus className="w-5 h-5" /> New Report
                        </button>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4 pb-8 border-b border-white/5">
                {[
                    { label: 'Category', val: 'Electronics' },
                    { label: 'Region', val: 'North America' },
                    { label: 'Timeframe', val: 'Last 30 Days' },
                ].map((filter) => (
                    <div key={filter.label} className="bg-white/[0.03] border border-white/10 px-4 py-2 rounded-2xl flex items-center gap-3 cursor-pointer hover:border-primary/50 transition-all">
                        <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">{filter.label}</span>
                        <span className="text-sm font-bold text-slate-200">{filter.val}</span>
                    </div>
                ))}
                <button className="text-xs font-black text-primary uppercase tracking-widest ml-4 hover:underline">Clear Filters</button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="bg-white/[0.03] border border-white/10 p-8 rounded-[2.5rem] relative group"
                    >
                        <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 blur-3xl rounded-full translate-x-12 -translate-y-12"></div>
                        <div className="flex items-center justify-between mb-6">
                            <p className="text-xs font-black uppercase text-slate-500 tracking-widest">{stat.label}</p>
                            <stat.icon className="w-5 h-5 text-primary opacity-50" />
                        </div>
                        <div className="flex items-end gap-3 relative z-10">
                            <h3 className="text-3xl font-black">{stat.value}</h3>
                            {stat.trend && (
                                <span className={`text-sm font-bold flex items-center mb-1 ${stat.trend > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {stat.trend > 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                                    {Math.abs(stat.trend)}%
                                </span>
                            )}
                            {stat.status && (
                                <span className="px-2 py-0.5 rounded bg-primary text-background-dark text-[10px] font-black uppercase mb-1">{stat.status}</span>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                <div className="xl:col-span-2 bg-white/[0.03] border border-white/10 p-10 rounded-[3rem] shadow-2xl overflow-hidden relative group">
                    <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
                    <div className="flex items-center justify-between mb-12">
                        <div>
                            <h4 className="text-2xl font-bold">Trend Velocity</h4>
                            <p className="text-slate-500 font-medium">Interaction vs. Interest over time</p>
                        </div>
                        <div className="flex gap-6">
                            <div className="flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-primary shadow-[0_0_10px_rgba(13,204,242,0.5)]"></span>
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Interest</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-white/20"></span>
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Baseline</span>
                            </div>
                        </div>
                    </div>

                    <div className="h-64 w-full relative group/chart">
                        <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 1000 200">
                            <defs>
                                <linearGradient id="chartGrad" x1="0" x2="0" y1="0" y2="1">
                                    <stop offset="0%" stopColor="#0dccf2" stopOpacity="0.3" />
                                    <stop offset="100%" stopColor="#0dccf2" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <motion.path
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 2, ease: "easeInOut" }}
                                d="M0,150 Q100,140 200,160 T400,120 T600,80 T800,100 T1000,40"
                                fill="none" stroke="#0dccf2" strokeWidth="4" strokeLinecap="round"
                            />
                            <path d="M0,150 Q100,140 200,160 T400,120 T600,80 T800,100 T1000,40 V200 H0 Z" fill="url(#chartGrad)" />
                        </svg>
                        <div className="mt-6 flex justify-between text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] border-t border-white/5 pt-4">
                            {['01 Aug', '08 Aug', '15 Aug', '22 Aug', '29 Aug'].map(d => <span key={d}>{d}</span>)}
                        </div>
                    </div>
                </div>

                <div className="bg-white/[0.03] border border-white/10 p-10 rounded-[3rem] shadow-2xl">
                    <h4 className="text-2xl font-bold mb-10">Growing Products</h4>
                    <div className="space-y-8">
                        {products.map((p) => (
                            <div key={p.rank} className="flex items-center gap-4 group">
                                <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-primary font-black text-lg group-hover:bg-primary group-hover:text-background-dark transition-all duration-500">
                                    {p.rank}
                                </div>
                                <div className="flex-1">
                                    <p className="font-bold text-white group-hover:text-primary transition-colors">{p.name}</p>
                                    <p className="text-xs text-slate-500 font-medium">{p.cat} • High Demand</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-black text-emerald-400">+{p.growth}%</p>
                                    <div className="w-16 h-1.5 bg-white/5 rounded-full mt-2 overflow-hidden border border-white/5">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            whileInView={{ width: `${p.val}%` }}
                                            className="h-full bg-emerald-400 rounded-full"
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                        <button className="w-full mt-4 py-4 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black text-primary uppercase tracking-widest hover:bg-white/10 transition-all">
                            View All Rankings
                        </button>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default MarketTrends;

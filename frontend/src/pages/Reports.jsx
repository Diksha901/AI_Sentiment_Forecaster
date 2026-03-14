import React from 'react';
import { motion } from 'framer-motion';
import { Download, Plus, Search, Filter, FileText, PieChart, BarChart2, Archive, Trash2, ExternalLink } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';

const Reports = () => {
    const reports = [
        { id: 1, title: 'Q3 Consumer Behavior Analysis', date: 'Oct 24, 2023', size: '4.2 MB', tags: ['Retail', 'Growth'], icon: PieChart, color: 'text-primary' },
        { id: 2, title: 'European Tech Adoption Trends', date: 'Oct 18, 2023', size: '1.8 MB', tags: ['Europe', 'Tech'], icon: BarChart2, color: 'text-emerald-400' },
        { id: 3, title: 'Supply Chain Risk Assessment', date: 'Oct 12, 2023', size: '3.5 MB', tags: ['Logistics', 'Risk'], icon: FileText, color: 'text-amber-400' },
        { id: 4, title: 'Market Entrance: Southeast Asia', date: 'Sep 22, 2023', size: '5.1 MB', tags: ['Expansion', 'SEA'], icon: ExternalLink, color: 'text-violet-400' },
    ];

    return (
        <DashboardLayout title="Reports">
            <div className="space-y-10">
                {/* Header */}
                <div className="flex flex-wrap justify-between items-end gap-8">
                    <div className="max-w-2xl">
                        <h1 className="text-4xl font-black text-white tracking-tight mb-3">Reports</h1>
                        <p className="text-slate-400 text-lg leading-relaxed">Manage, export, and analyze your AI-generated market trends.</p>
                    </div>
                    <button className="flex items-center gap-3 px-8 py-4 bg-primary text-background-dark font-black rounded-2xl hover:scale-105 transition-all shadow-xl shadow-primary/20">
                        <Plus className="w-6 h-6" /> Generate New Report
                    </button>
                </div>

                {/* Filters */}
                <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
                    <div className="relative w-full md:max-w-md group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors w-5 h-5" />
                        <input
                            className="w-full pl-12 pr-6 py-4 bg-white/[0.03] border border-white/10 rounded-2xl focus:ring-2 focus:ring-primary/50 outline-none text-sm transition-all"
                            placeholder="Search reports by name, tag, or date..."
                        />
                    </div>
                    <div className="flex items-center gap-4 w-full md:w-auto">
                        <div className="flex p-1.5 bg-white/[0.03] border border-white/10 rounded-2xl">
                            {['All', 'Exported', 'Archived'].map((tab, i) => (
                                <button key={tab} className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${i === 0 ? 'bg-primary text-background-dark' : 'text-slate-500 hover:text-white'}`}>
                                    {tab}
                                </button>
                            ))}
                        </div>
                        <button className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-primary/50 transition-all">
                            <Filter className="w-5 h-5 text-primary" />
                        </button>
                    </div>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                    {reports.map((report, i) => (
                        <motion.div
                            key={report.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="group bg-white/[0.02] border border-white/10 p-8 rounded-[2.5rem] hover:border-primary/50 transition-all relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl rounded-full translate-x-16 -translate-y-16"></div>
                            <div className="flex justify-between items-start mb-8 relative z-10">
                                <div className={`p-4 bg-white/5 rounded-2xl ${report.color}`}>
                                    <report.icon className="w-6 h-6" />
                                </div>
                                <div className="flex gap-2">
                                    <button className="p-2 text-slate-500 hover:text-primary transition-colors"><Download className="w-4 h-4" /></button>
                                    <button className="p-2 text-slate-500 hover:text-primary transition-colors"><Archive className="w-4 h-4" /></button>
                                </div>
                            </div>
                            <h3 className="font-bold text-xl mb-2 group-hover:text-primary transition-colors">{report.title}</h3>
                            <p className="text-xs text-slate-500 font-medium mb-6">Generated on {report.date} • {report.size}</p>
                            <div className="flex flex-wrap gap-2 mb-8">
                                {report.tags.map(tag => (
                                    <span key={tag} className="px-3 py-1 bg-white/5 border border-white/5 text-[10px] font-black rounded-lg uppercase tracking-wider text-slate-400">{tag}</span>
                                ))}
                            </div>
                            <button className="w-full py-4 bg-white/5 border border-white/10 hover:bg-primary hover:text-background-dark font-black rounded-2xl text-xs uppercase tracking-[0.2em] transition-all">
                                View Full Report
                            </button>
                        </motion.div>
                    ))}

                    {/* New Analysis Card */}
                    <div className="border-2 border-dashed border-white/10 rounded-[2.5rem] p-8 flex flex-col items-center justify-center text-center gap-6 group hover:border-primary/50 transition-all cursor-pointer">
                        <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-slate-600 group-hover:text-primary group-hover:bg-primary/10 transition-all duration-500">
                            <Plus className="w-8 h-8" />
                        </div>
                        <div>
                            <p className="font-bold text-lg text-white">Start a new analysis</p>
                            <p className="text-sm text-slate-500 mt-1">Pick a sector and let AI do the work</p>
                        </div>
                        <button className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline">Launch Wizard</button>
                    </div>
                </div>

                {/* Footer Stats */}
                <div className="bg-white/[0.02] border border-white/10 p-10 rounded-[3rem] flex flex-wrap items-center justify-between gap-10">
                    <div className="flex items-center gap-12">
                        {[
                            { label: 'Total Reports', val: '24' },
                            { label: 'Exported this Month', val: '12' },
                            { label: 'AI Tokens Used', val: '8.4k' },
                        ].map(stat => (
                            <div key={stat.label}>
                                <p className="text-[10px] uppercase font-black tracking-[0.2em] text-slate-500 mb-2">{stat.label}</p>
                                <p className="text-3xl font-black">{stat.val}</p>
                            </div>
                        ))}
                    </div>
                    <div className="flex gap-4">
                        <button className="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-white/10 transition-all">Batch Export</button>
                        <button className="px-8 py-4 bg-white text-background-dark rounded-2xl text-xs font-black uppercase tracking-widest hover:scale-105 transition-all">Download All (ZIP)</button>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default Reports;

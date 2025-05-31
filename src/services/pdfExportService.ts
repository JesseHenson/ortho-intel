import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import type { AnalysisResult, StrategicOpportunity } from '../lib/api';

export interface PDFExportOptions {
  clientName?: string;
  analystName?: string;
  includeWatermark?: boolean;
  customBranding?: {
    logoUrl?: string;
    primaryColor?: string;
    companyName?: string;
  };
  sections?: {
    executiveSummary?: boolean;
    opportunities?: boolean;
    sourceEvidence?: boolean;
    marketAnalysis?: boolean;
  };
}

export class PDFExportService {
  private static instance: PDFExportService;
  
  public static getInstance(): PDFExportService {
    if (!PDFExportService.instance) {
      PDFExportService.instance = new PDFExportService();
    }
    return PDFExportService.instance;
  }

  async exportAnalysisReport(
    analysisResult: AnalysisResult,
    options: PDFExportOptions = {}
  ): Promise<void> {
    const {
      clientName = 'Client Organization',
      analystName = 'Orthopedic Intelligence Team',
      includeWatermark = false,
      customBranding = {},
      sections = {
        executiveSummary: true,
        opportunities: true,
        sourceEvidence: true,
        marketAnalysis: true
      }
    } = options;

    // Create new PDF document
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    let currentY = margin;

    // Add header
    await this.addHeader(pdf, pageWidth, currentY, customBranding);
    currentY += 40;

    // Add client information
    currentY = this.addClientInfo(pdf, currentY, clientName, analystName, analysisResult.analysis_id);
    currentY += 20;

    // Add executive summary
    if (sections.executiveSummary) {
      currentY = await this.addExecutiveSummary(pdf, currentY, pageWidth, margin, analysisResult);
      currentY += 15;
    }

    // Add strategic opportunities
    if (sections.opportunities) {
      currentY = await this.addStrategicOpportunities(pdf, currentY, pageWidth, margin, analysisResult.top_opportunities);
    }

    // Add market analysis if requested
    if (sections.marketAnalysis) {
      currentY = await this.addMarketAnalysis(pdf, currentY, pageWidth, margin, analysisResult);
    }

    // Add watermark if requested
    if (includeWatermark) {
      this.addWatermark(pdf, pageWidth, pageHeight);
    }

    // Add footer
    this.addFooter(pdf, pageWidth, pageHeight, analysisResult.analysis_id);

    // Download the PDF
    const fileName = `orthopedic-intelligence-report-${analysisResult.analysis_id}-${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
  }

  private async addHeader(
    pdf: jsPDF,
    pageWidth: number,
    y: number,
    branding: PDFExportOptions['customBranding'] = {}
  ): Promise<void> {
    const { logoUrl, primaryColor = '#2563eb', companyName = 'Orthopedic Intelligence' } = branding;

    // Set header background
    pdf.setFillColor(244, 244, 245); // gray-100
    pdf.rect(0, 0, pageWidth, 50, 'F');

    // Add company logo or name
    pdf.setFontSize(24);
    pdf.setTextColor(40, 40, 40);
    pdf.setFont(undefined, 'bold');
    pdf.text(companyName, 20, 25);

    // Add subtitle
    pdf.setFontSize(12);
    pdf.setTextColor(100, 100, 100);
    pdf.setFont(undefined, 'normal');
    pdf.text('Competitive Intelligence Report', 20, 35);

    // Add generation date
    pdf.setFontSize(10);
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, pageWidth - 60, 35);
  }

  private addClientInfo(
    pdf: jsPDF,
    y: number,
    clientName: string,
    analystName: string,
    analysisId: string
  ): number {
    pdf.setFontSize(12);
    pdf.setTextColor(60, 60, 60);
    pdf.setFont(undefined, 'normal');

    pdf.text(`Prepared For: ${clientName}`, 20, y);
    pdf.text(`Analyst: ${analystName}`, 20, y + 8);
    pdf.text(`Analysis ID: ${analysisId}`, 20, y + 16);

    return y + 16;
  }

  private async addExecutiveSummary(
    pdf: jsPDF,
    y: number,
    pageWidth: number,
    margin: number,
    analysisResult: AnalysisResult
  ): Promise<number> {
    let currentY = y;

    // Section header
    pdf.setFontSize(16);
    pdf.setTextColor(40, 40, 40);
    pdf.setFont(undefined, 'bold');
    pdf.text('Executive Summary', margin, currentY);
    currentY += 12;

    // Key insight
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text('Key Insight:', margin, currentY);
    currentY += 8;

    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);
    const keyInsightLines = pdf.splitTextToSize(
      analysisResult.executive_summary.key_insight,
      pageWidth - 2 * margin
    );
    pdf.text(keyInsightLines, margin, currentY);
    currentY += keyInsightLines.length * 6 + 10;

    // Key metrics
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.setTextColor(40, 40, 40);
    pdf.text('Key Metrics:', margin, currentY);
    currentY += 8;

    // Metrics in a box
    const metricsBoxY = currentY;
    const metricsBoxHeight = 30;
    pdf.setFillColor(248, 250, 252); // blue-50
    pdf.rect(margin, metricsBoxY, pageWidth - 2 * margin, metricsBoxHeight, 'F');

    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);
    
    const col1X = margin + 10;
    const col2X = margin + (pageWidth - 2 * margin) / 3;
    const col3X = margin + 2 * (pageWidth - 2 * margin) / 3;

    pdf.text(`Confidence Score: ${analysisResult.confidence_score}/10`, col1X, metricsBoxY + 10);
    pdf.text(`Total Opportunities: ${analysisResult.top_opportunities.length}`, col2X, metricsBoxY + 10);
    pdf.text(`Sources Analyzed: ${analysisResult.metadata.total_sources}`, col3X, metricsBoxY + 10);

    const highValueOpps = analysisResult.top_opportunities.filter(opp => opp.opportunity_score >= 8.5).length;
    pdf.text(`High-Value Opportunities: ${highValueOpps}`, col1X, metricsBoxY + 20);
    pdf.text(`Focus Area: ${analysisResult.metadata.focus_area}`, col2X, metricsBoxY + 20);
    pdf.text(`Analysis Type: ${analysisResult.metadata.analysis_type}`, col3X, metricsBoxY + 20);

    currentY += metricsBoxHeight + 15;

    // Strategic recommendations
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.setTextColor(40, 40, 40);
    pdf.text('Strategic Recommendations:', margin, currentY);
    currentY += 8;

    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);

    analysisResult.executive_summary.strategic_recommendations.forEach((rec, index) => {
      const bulletPoint = `• ${rec}`;
      const lines = pdf.splitTextToSize(bulletPoint, pageWidth - 2 * margin - 10);
      pdf.text(lines, margin + 10, currentY);
      currentY += lines.length * 5 + 2;
    });

    return currentY;
  }

  private async addStrategicOpportunities(
    pdf: jsPDF,
    y: number,
    pageWidth: number,
    margin: number,
    opportunities: StrategicOpportunity[]
  ): Promise<number> {
    let currentY = y;

    // Check if we need a new page
    if (currentY > 200) {
      pdf.addPage();
      currentY = margin;
    }

    // Section header
    pdf.setFontSize(16);
    pdf.setTextColor(40, 40, 40);
    pdf.setFont(undefined, 'bold');
    pdf.text(`Strategic Opportunities (${opportunities.length})`, margin, currentY);
    currentY += 15;

    // Add each opportunity
    opportunities.slice(0, 3).forEach((opportunity, index) => {
      // Check if we need a new page for this opportunity
      if (currentY > 220) {
        pdf.addPage();
        currentY = margin;
      }

      // Opportunity header
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(40, 40, 40);
      const title = `${index + 1}. ${opportunity.title}`;
      pdf.text(title, margin, currentY);
      currentY += 10;

      // Score badge
      pdf.setFontSize(10);
      pdf.setFillColor(34, 197, 94); // green-500
      pdf.rect(margin, currentY, 30, 8, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.text(`Score: ${opportunity.opportunity_score.toFixed(1)}`, margin + 2, currentY + 6);
      currentY += 12;

      // Description
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(60, 60, 60);
      const descLines = pdf.splitTextToSize(
        opportunity.description.substring(0, 300) + (opportunity.description.length > 300 ? '...' : ''),
        pageWidth - 2 * margin
      );
      pdf.text(descLines, margin, currentY);
      currentY += descLines.length * 5 + 8;

      // Key details in a grid
      const detailsY = currentY;
      pdf.setFillColor(250, 250, 250);
      pdf.rect(margin, detailsY, pageWidth - 2 * margin, 20, 'F');

      pdf.setFontSize(9);
      pdf.setTextColor(80, 80, 80);
      const detailCol1 = margin + 5;
      const detailCol2 = margin + (pageWidth - 2 * margin) / 3;
      const detailCol3 = margin + 2 * (pageWidth - 2 * margin) / 3;

      pdf.text(`Time to Market: ${opportunity.time_to_market}`, detailCol1, detailsY + 8);
      pdf.text(`Investment: ${opportunity.investment_level}`, detailCol2, detailsY + 8);
      pdf.text(`Implementation: ${opportunity.implementation_difficulty}`, detailCol3, detailsY + 8);

      pdf.text(`Market Size: ${opportunity.market_size}`, detailCol1, detailsY + 15);
      pdf.text(`Category: ${opportunity.category}`, detailCol2, detailsY + 15);

      currentY += 25;

      // Next steps (first 3)
      if (opportunity.next_steps && opportunity.next_steps.length > 0) {
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(40, 40, 40);
        pdf.text('Key Next Steps:', margin, currentY);
        currentY += 6;

        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(9);
        opportunity.next_steps.slice(0, 3).forEach((step, stepIndex) => {
          const stepText = `${stepIndex + 1}. ${step}`;
          const stepLines = pdf.splitTextToSize(stepText, pageWidth - 2 * margin - 10);
          pdf.text(stepLines, margin + 5, currentY);
          currentY += stepLines.length * 4 + 2;
        });
      }

      currentY += 10; // Space between opportunities
    });

    return currentY;
  }

  private async addMarketAnalysis(
    pdf: jsPDF,
    y: number,
    pageWidth: number,
    margin: number,
    analysisResult: AnalysisResult
  ): Promise<number> {
    let currentY = y;

    // Check if we need a new page
    if (currentY > 220) {
      pdf.addPage();
      currentY = margin;
    }

    // Section header
    pdf.setFontSize(16);
    pdf.setTextColor(40, 40, 40);
    pdf.setFont(undefined, 'bold');
    pdf.text('Market Analysis Summary', margin, currentY);
    currentY += 15;

    // Revenue potential
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.text('Revenue Potential:', margin, currentY);
    currentY += 8;

    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);
    const revenueLines = pdf.splitTextToSize(
      analysisResult.executive_summary.revenue_potential,
      pageWidth - 2 * margin
    );
    pdf.text(revenueLines, margin, currentY);
    currentY += revenueLines.length * 5 + 10;

    // Market share opportunity
    pdf.setFontSize(12);
    pdf.setFont(undefined, 'bold');
    pdf.setTextColor(40, 40, 40);
    pdf.text('Market Share Opportunity:', margin, currentY);
    currentY += 8;

    pdf.setFontSize(10);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);
    const marketLines = pdf.splitTextToSize(
      analysisResult.executive_summary.market_share_opportunity,
      pageWidth - 2 * margin
    );
    pdf.text(marketLines, margin, currentY);
    currentY += marketLines.length * 5 + 10;

    return currentY;
  }

  private addWatermark(pdf: jsPDF, pageWidth: number, pageHeight: number): void {
    pdf.setTextColor(200, 200, 200);
    pdf.setFontSize(50);
    pdf.setFont(undefined, 'bold');
    
    // Add rotated watermark
    pdf.text('CONFIDENTIAL', pageWidth / 2, pageHeight / 2, {
      angle: 45,
      align: 'center'
    });
  }

  private addFooter(pdf: jsPDF, pageWidth: number, pageHeight: number, analysisId: string): void {
    const footerY = pageHeight - 15;
    
    pdf.setFontSize(8);
    pdf.setTextColor(120, 120, 120);
    pdf.setFont(undefined, 'normal');
    
    pdf.text('© 2024 Orthopedic Intelligence Platform - Confidential and Proprietary', 20, footerY);
    pdf.text(`Report ID: ${analysisId}`, pageWidth - 50, footerY);
    
    // Add page number
    const pageCount = pdf.getNumberOfPages();
    pdf.text(`Page 1 of ${pageCount}`, pageWidth - 30, footerY - 5);
  }

  async exportOpportunitySnapshot(
    opportunity: StrategicOpportunity,
    options: Omit<PDFExportOptions, 'sections'> = {}
  ): Promise<void> {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;

    // Add header
    await this.addHeader(pdf, pageWidth, 20, options.customBranding);

    // Add opportunity details
    let currentY = 70;
    
    pdf.setFontSize(18);
    pdf.setTextColor(40, 40, 40);
    pdf.setFont(undefined, 'bold');
    pdf.text('Strategic Opportunity Snapshot', margin, currentY);
    currentY += 15;

    pdf.setFontSize(16);
    pdf.text(opportunity.title, margin, currentY);
    currentY += 12;

    // Score
    pdf.setFillColor(34, 197, 94);
    pdf.rect(margin, currentY, 40, 10, 'F');
    pdf.setFontSize(12);
    pdf.setTextColor(255, 255, 255);
    pdf.text(`Score: ${opportunity.opportunity_score.toFixed(1)}/10`, margin + 2, currentY + 7);
    currentY += 20;

    // Description
    pdf.setFontSize(11);
    pdf.setFont(undefined, 'normal');
    pdf.setTextColor(60, 60, 60);
    const descLines = pdf.splitTextToSize(opportunity.description, pageWidth - 2 * margin);
    pdf.text(descLines, margin, currentY);
    currentY += descLines.length * 6 + 15;

    // Key details
    const details = [
      ['Time to Market', opportunity.time_to_market],
      ['Investment Level', opportunity.investment_level],
      ['Implementation Difficulty', opportunity.implementation_difficulty],
      ['Market Size', opportunity.market_size],
      ['Category', opportunity.category]
    ];

    details.forEach(([label, value]) => {
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(40, 40, 40);
      pdf.text(`${label}:`, margin, currentY);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(60, 60, 60);
      pdf.text(value, margin + 50, currentY);
      currentY += 8;
    });

    // Add footer
    this.addFooter(pdf, pageWidth, pageHeight, `snapshot-${Date.now()}`);

    // Download
    const fileName = `opportunity-${opportunity.title.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
  }
}

export const pdfExportService = PDFExportService.getInstance(); 
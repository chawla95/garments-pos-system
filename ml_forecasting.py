"""
Analytics Module for Demand Forecasting and Inventory Optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import models
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class InventoryAnalytics:
    def __init__(self):
        pass
        
    def prepare_sales_data(self, db: Session, product_id: int, days_back: int = 90) -> pd.DataFrame:
        """Prepare historical sales data for analysis"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get sales data from invoice items
        sales_data = db.query(
            models.InvoiceItem.product_name,
            models.InvoiceItem.quantity,
            models.Invoice.created_at,
            models.InvoiceItem.inventory_item_id
        ).join(
            models.Invoice, models.InvoiceItem.invoice_id == models.Invoice.id
        ).filter(
            and_(
                models.InvoiceItem.inventory_item_id.in_(
                    db.query(models.InventoryItem.id).filter(
                        models.InventoryItem.product_id == product_id
                    )
                ),
                models.Invoice.created_at >= cutoff_date
            )
        ).all()
        
        if not sales_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': sale.created_at.date(),
                'quantity': sale.quantity,
                'product_name': sale.product_name
            }
            for sale in sales_data
        ])
        
        # Group by date and sum quantities
        df = df.groupby('date')['quantity'].sum().reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        return df
    
    def analyze_product(self, db: Session, product_id: int) -> Dict:
        """Analyze a product for demand forecasting and inventory optimization"""
        # Get product info
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return {}
        
        # Get current inventory
        current_inventory = int(db.query(func.sum(models.InventoryItem.quantity)).filter(
            models.InventoryItem.product_id == product_id
        ).scalar() or 0)
        
        # Get sales data
        sales_df = self.prepare_sales_data(db, product_id)
        
        # Calculate basic metrics
        total_sales = int(sales_df['quantity'].sum()) if not sales_df.empty else 0
        avg_daily_sales = float(sales_df['quantity'].mean()) if not sales_df.empty else 0
        days_with_sales = int(len(sales_df)) if not sales_df.empty else 0
        
        # Get last sale date
        last_sale_date = None
        days_since_last_sale = None
        if not sales_df.empty:
            last_sale_date = sales_df['date'].max()
            days_since_last_sale = (datetime.now().date() - last_sale_date.date()).days
        
        # Simple demand forecasting based on average sales
        forecast_30d = []
        forecast_90d = []
        if avg_daily_sales > 0:
            # Simple forecast: average daily sales * number of days
            forecast_30d = [avg_daily_sales] * 30
            forecast_90d = [avg_daily_sales] * 90
        
        # Calculate reorder suggestions
        reorder_quantity = 0
        reorder_date = None
        
        if avg_daily_sales > 0:
            safety_stock = avg_daily_sales * 7  # 7 days safety stock
            reorder_point = avg_daily_sales * 7 + safety_stock  # 7 days lead time
            
            if current_inventory <= reorder_point:
                reorder_quantity = int(avg_daily_sales * 30)  # 30 days supply
                reorder_date = datetime.now().date()
        
        # Determine stock status
        stock_status = "NORMAL"
        if days_since_last_sale and days_since_last_sale > 60:
            stock_status = "DEADSTOCK"
        elif days_since_last_sale and days_since_last_sale > 30:
            stock_status = "SLOW_MOVING"
        elif current_inventory == 0:
            stock_status = "OUT_OF_STOCK"
        
        return {
            "product_id": int(product_id),
            "product_name": str(product.name),
            "current_inventory": int(current_inventory),
            "total_sales": int(total_sales),
            "avg_daily_sales": float(round(avg_daily_sales, 2)),
            "days_with_sales": int(days_with_sales),
            "last_sale_date": last_sale_date.isoformat() if last_sale_date else None,
            "days_since_last_sale": int(days_since_last_sale) if days_since_last_sale else None,
            "stock_status": str(stock_status),
            "model_trained": bool(avg_daily_sales > 0),
            "forecast_30d": [float(x) for x in forecast_30d],
            "forecast_90d": [float(x) for x in forecast_90d],
            "reorder_quantity": int(reorder_quantity),
            "reorder_date": reorder_date.isoformat() if reorder_date else None,
            "avg_forecast_demand": float(round(avg_daily_sales, 2)) if avg_daily_sales > 0 else 0.0
        }
    
    def get_inventory_analysis(self, db: Session) -> Dict:
        """Get comprehensive inventory analysis for all products"""
        products = db.query(models.Product).all()
        
        analysis_results = []
        deadstock_items = []
        slow_moving_items = []
        out_of_stock_items = []
        
        for product in products:
            analysis = self.analyze_product(db, product.id)
            if analysis:
                analysis_results.append(analysis)
                
                # Categorize items
                if analysis['stock_status'] == 'DEADSTOCK':
                    deadstock_items.append(analysis)
                elif analysis['stock_status'] == 'SLOW_MOVING':
                    slow_moving_items.append(analysis)
                elif analysis['stock_status'] == 'OUT_OF_STOCK':
                    out_of_stock_items.append(analysis)
        
        return {
            "total_products": int(len(analysis_results)),
            "products_analyzed": analysis_results,
            "deadstock_count": int(len(deadstock_items)),
            "slow_moving_count": int(len(slow_moving_items)),
            "out_of_stock_count": int(len(out_of_stock_items)),
            "deadstock_items": deadstock_items,
            "slow_moving_items": slow_moving_items,
            "out_of_stock_items": out_of_stock_items
        }
    
    def get_reorder_suggestions(self, db: Session) -> List[Dict]:
        """Get reorder suggestions for products that need restocking"""
        products = db.query(models.Product).all()
        
        suggestions = []
        for product in products:
            analysis = self.analyze_product(db, product.id)
            if analysis and analysis.get('reorder_quantity', 0) > 0:
                suggestions.append({
                    "product_id": int(product.id),
                    "product_name": str(product.name),
                    "reorder_quantity": int(analysis['reorder_quantity']),
                    "reorder_date": analysis['reorder_date'],
                    "current_inventory": int(analysis['current_inventory']),
                    "avg_forecast_demand": float(analysis['avg_forecast_demand'])
                })
        
        return suggestions

# Alias for backward compatibility
InventoryOptimizer = InventoryAnalytics 
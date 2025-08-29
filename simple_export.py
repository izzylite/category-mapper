#!/usr/bin/env python3
"""
Simple export of categories from database
"""
import json
import psycopg2
import time
from datetime import datetime

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect('postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:5433/aicategorymapping')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def export_level_categories(level_num):
    """Export categories for a specific level"""
    try:
        conn = psycopg2.connect('postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:5433/aicategorymapping')
        cursor = conn.cursor()
        
        query = f"SELECT level{level_num}_id, category_name FROM categories_level{level_num} ORDER BY category_name;"
        cursor.execute(query)
        results = cursor.fetchall()
        
        categories = []
        for row in results:
            categories.append({
                "id": row[0],
                "name": row[1]
            })
        
        cursor.close()
        conn.close()
        
        print(f"✅ Exported {len(categories)} Level {level_num} categories")
        return categories
        
    except Exception as e:
        print(f"❌ Error exporting Level {level_num}: {e}")
        return []

def export_hierarchical_sample():
    """Export a sample of hierarchical categories"""
    try:
        conn = psycopg2.connect('postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:5433/aicategorymapping')
        cursor = conn.cursor()
        
        query = """
        SELECT 
            l1.category_name AS level1_name,
            l2.category_name AS level2_name,
            l3.category_name AS level3_name
        FROM categories_level1 l1
        LEFT JOIN categories_level2 l2 ON l1.level1_id = l2.level1_parent
        LEFT JOIN categories_level3 l3 ON l2.level2_id = l3.level2_parent
        ORDER BY l1.category_name, l2.category_name, l3.category_name
        LIMIT 50;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        hierarchical = []
        for row in results:
            path_parts = []
            if row[0]: path_parts.append(row[0])
            if row[1]: path_parts.append(row[1])
            if row[2]: path_parts.append(row[2])
            
            if path_parts:
                hierarchical.append({
                    "level1": row[0],
                    "level2": row[1],
                    "level3": row[2],
                    "path": " > ".join(path_parts),
                    "depth": len(path_parts)
                })
        
        cursor.close()
        conn.close()
        
        print(f"✅ Exported {len(hierarchical)} hierarchical category samples")
        return hierarchical
        
    except Exception as e:
        print(f"❌ Error exporting hierarchical categories: {e}")
        return []

def main():
    print("🚀 Simple Category Export")
    print("=" * 40)
    
    # Test connection first
    if not test_connection():
        print("💥 Cannot connect to database")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Initialize export data
    export_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "database": "aicategorymapping",
            "type": "simple_export"
        },
        "categories_by_level": {},
        "hierarchical_sample": [],
        "statistics": {}
    }
    
    # Export each level
    for level in range(1, 8):
        print(f"📋 Exporting Level {level}...")
        categories = export_level_categories(level)
        export_data['categories_by_level'][f'level{level}'] = categories
        time.sleep(0.5)  # Small delay between queries
    
    # Export hierarchical sample
    print("🌳 Exporting hierarchical sample...")
    export_data['hierarchical_sample'] = export_hierarchical_sample()
    
    # Generate statistics
    export_data['statistics'] = {
        f"level{i}_count": len(export_data['categories_by_level'][f'level{i}']) 
        for i in range(1, 8)
    }
    export_data['statistics']['total_categories'] = sum(export_data['statistics'].values())
    export_data['statistics']['hierarchical_sample_count'] = len(export_data['hierarchical_sample'])
    
    # Save to JSON
    output_file = "categories_simple_export.json"
    print(f"💾 Saving to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Export completed!")
    print(f"\n📊 Statistics:")
    for key, value in export_data['statistics'].items():
        print(f"   {key}: {value}")
    
    # Show sample categories
    print(f"\n📋 Sample Level 1 Categories:")
    for i, cat in enumerate(export_data['categories_by_level']['level1'][:5]):
        print(f"   {i+1}. {cat['name']}")
    
    if len(export_data['categories_by_level']['level1']) > 5:
        print(f"   ... and {len(export_data['categories_by_level']['level1']) - 5} more")

if __name__ == "__main__":
    main()

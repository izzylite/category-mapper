#!/usr/bin/env python3
"""
Export all categories from the database to JSON
"""
import json
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

def export_all_categories():
    """Export all categories and related data to JSON"""
    try:
        # Connect to database
        connection_string = os.getenv('POSTGRES_CONNECTION_STRING')
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        print("🔗 Connected to database successfully!")
        
        # Initialize the export data structure
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "database": "aicategorymapping",
                "description": "Complete export of all categories and related data"
            },
            "categories": {
                "hierarchical": [],
                "by_level": {
                    "level1": [],
                    "level2": [],
                    "level3": [],
                    "level4": [],
                    "level5": [],
                    "level6": [],
                    "level7": []
                }
            },
            "logic_rules": {
                "hard_logic": [],
                "soft_logic": []
            },
            "explanations": [],
            "statistics": {}
        }
        
        print("📊 Exporting hierarchical categories...")
        
        # Export hierarchical categories (complete tree structure)
        hierarchical_query = """
        SELECT 
            l1.level1_id, l1.category_name AS level1_name,
            l2.level2_id, l2.category_name AS level2_name,
            l3.level3_id, l3.category_name AS level3_name,
            l4.level4_id, l4.category_name AS level4_name,
            l5.level5_id, l5.category_name AS level5_name,
            l6.level6_id, l6.category_name AS level6_name,
            l7.level7_id, l7.category_name AS level7_name
        FROM categories_level1 l1
        LEFT JOIN categories_level2 l2 ON l1.level1_id = l2.level1_parent
        LEFT JOIN categories_level3 l3 ON l2.level2_id = l3.level2_parent
        LEFT JOIN categories_level4 l4 ON l3.level3_id = l4.level3_parent
        LEFT JOIN categories_level5 l5 ON l4.level4_id = l5.level4_parent
        LEFT JOIN categories_level6 l6 ON l5.level5_id = l6.level5_parent
        LEFT JOIN categories_level7 l7 ON l6.level6_id = l7.level6_parent
        ORDER BY l1.level1_id, l2.level2_id, l3.level3_id, l4.level4_id, l5.level5_id, l6.level6_id, l7.level7_id;
        """
        
        cursor.execute(hierarchical_query)
        hierarchical_results = cursor.fetchall()
        
        for row in hierarchical_results:
            category_path = {
                "level1": {"id": row[0], "name": row[1]} if row[0] else None,
                "level2": {"id": row[2], "name": row[3]} if row[2] else None,
                "level3": {"id": row[4], "name": row[5]} if row[4] else None,
                "level4": {"id": row[6], "name": row[7]} if row[6] else None,
                "level5": {"id": row[8], "name": row[9]} if row[8] else None,
                "level6": {"id": row[10], "name": row[11]} if row[10] else None,
                "level7": {"id": row[12], "name": row[13]} if row[12] else None,
            }
            
            # Create path string
            path_parts = []
            for level in ['level1', 'level2', 'level3', 'level4', 'level5', 'level6', 'level7']:
                if category_path[level]:
                    path_parts.append(category_path[level]['name'])
                else:
                    break
            
            category_path['path'] = ' > '.join(path_parts)
            category_path['depth'] = len(path_parts)
            
            export_data['categories']['hierarchical'].append(category_path)
        
        print(f"   ✅ Exported {len(hierarchical_results)} hierarchical category paths")
        
        # Export categories by individual levels
        for level_num in range(1, 8):
            print(f"📋 Exporting Level {level_num} categories...")
            
            level_query = f"""
            SELECT level{level_num}_id, category_name 
            FROM categories_level{level_num} 
            ORDER BY category_name;
            """
            
            cursor.execute(level_query)
            level_results = cursor.fetchall()
            
            level_categories = []
            for row in level_results:
                level_categories.append({
                    "id": row[0],
                    "name": row[1]
                })
            
            export_data['categories']['by_level'][f'level{level_num}'] = level_categories
            print(f"   ✅ Exported {len(level_categories)} Level {level_num} categories")
        
        # Export hard logic rules
        print("🔧 Exporting hard logic rules...")
        hard_logic_query = """
        SELECT hl.word, hl.is_pattern,
               l1.category_name AS level1_name,
               l2.category_name AS level2_name,
               l3.category_name AS level3_name,
               l4.category_name AS level4_name,
               l5.category_name AS level5_name,
               l6.category_name AS level6_name,
               l7.category_name AS level7_name
        FROM new_category_hardlogic hl
        LEFT JOIN categories_level1 l1 ON hl.level1_id = l1.level1_id
        LEFT JOIN categories_level2 l2 ON hl.level2_id = l2.level2_id
        LEFT JOIN categories_level3 l3 ON hl.level3_id = l3.level3_id
        LEFT JOIN categories_level4 l4 ON hl.level4_id = l4.level4_id
        LEFT JOIN categories_level5 l5 ON hl.level5_id = l5.level5_id
        LEFT JOIN categories_level6 l6 ON hl.level6_id = l6.level6_id
        LEFT JOIN categories_level7 l7 ON hl.level7_id = l7.level7_id
        ORDER BY hl.word;
        """
        
        cursor.execute(hard_logic_query)
        hard_logic_results = cursor.fetchall()
        
        for row in hard_logic_results:
            # Build category path
            path_parts = []
            for i, level_name in enumerate(row[2:9]):  # Skip word and is_pattern
                if level_name:
                    path_parts.append(level_name)
            
            hard_logic_rule = {
                "word": row[0],
                "is_pattern": bool(row[1]),
                "category_path": ' > '.join(path_parts) if path_parts else None,
                "levels": {
                    "level1": row[2],
                    "level2": row[3],
                    "level3": row[4],
                    "level4": row[5],
                    "level5": row[6],
                    "level6": row[7],
                    "level7": row[8]
                }
            }
            
            export_data['logic_rules']['hard_logic'].append(hard_logic_rule)
        
        print(f"   ✅ Exported {len(hard_logic_results)} hard logic rules")
        
        # Export soft logic rules (KFS)
        print("🔧 Exporting soft logic rules...")
        soft_logic_query = """
        SELECT kfs.keyword,
               l1.category_name AS level1_name,
               l2.category_name AS level2_name,
               l3.category_name AS level3_name,
               l4.category_name AS level4_name,
               l5.category_name AS level5_name,
               l6.category_name AS level6_name,
               l7.category_name AS level7_name
        FROM new_category_kfs kfs
        LEFT JOIN categories_level1 l1 ON kfs.level1_id = l1.level1_id
        LEFT JOIN categories_level2 l2 ON kfs.level2_id = l2.level2_id
        LEFT JOIN categories_level3 l3 ON kfs.level3_id = l3.level3_id
        LEFT JOIN categories_level4 l4 ON kfs.level4_id = l4.level4_id
        LEFT JOIN categories_level5 l5 ON kfs.level5_id = l5.level5_id
        LEFT JOIN categories_level6 l6 ON kfs.level6_id = l6.level6_id
        LEFT JOIN categories_level7 l7 ON kfs.level7_id = l7.level7_id
        ORDER BY kfs.keyword;
        """
        
        cursor.execute(soft_logic_query)
        soft_logic_results = cursor.fetchall()
        
        for row in soft_logic_results:
            # Build category path
            path_parts = []
            for level_name in row[1:8]:  # Skip keyword
                if level_name:
                    path_parts.append(level_name)
            
            soft_logic_rule = {
                "keyword": row[0],
                "category_path": ' > '.join(path_parts) if path_parts else None,
                "levels": {
                    "level1": row[1],
                    "level2": row[2],
                    "level3": row[3],
                    "level4": row[4],
                    "level5": row[5],
                    "level6": row[6],
                    "level7": row[7]
                }
            }
            
            export_data['logic_rules']['soft_logic'].append(soft_logic_rule)
        
        print(f"   ✅ Exported {len(soft_logic_results)} soft logic rules")
        
        # Export category explanations
        print("📝 Exporting category explanations...")
        explanations_query = """
        SELECT ce.id, ce.explanation,
               l1.category_name AS level1_name,
               l2.category_name AS level2_name,
               l3.category_name AS level3_name,
               l4.category_name AS level4_name,
               l5.category_name AS level5_name,
               l6.category_name AS level6_name,
               l7.category_name AS level7_name
        FROM category_explanations ce
        LEFT JOIN categories_level1 l1 ON ce.level1_id = l1.level1_id
        LEFT JOIN categories_level2 l2 ON ce.level2_id = l2.level2_id
        LEFT JOIN categories_level3 l3 ON ce.level3_id = l3.level3_id
        LEFT JOIN categories_level4 l4 ON ce.level4_id = l4.level4_id
        LEFT JOIN categories_level5 l5 ON ce.level5_id = l5.level5_id
        LEFT JOIN categories_level6 l6 ON ce.level6_id = l6.level6_id
        LEFT JOIN categories_level7 l7 ON ce.level7_id = l7.level7_id
        ORDER BY ce.id;
        """
        
        cursor.execute(explanations_query)
        explanations_results = cursor.fetchall()
        
        for row in explanations_results:
            # Build category path
            path_parts = []
            for level_name in row[2:9]:  # Skip id and explanation
                if level_name:
                    path_parts.append(level_name)
            
            explanation = {
                "id": row[0],
                "explanation": row[1],
                "category_path": ' > '.join(path_parts) if path_parts else None,
                "levels": {
                    "level1": row[2],
                    "level2": row[3],
                    "level3": row[4],
                    "level4": row[5],
                    "level5": row[6],
                    "level6": row[7],
                    "level7": row[8]
                }
            }
            
            export_data['explanations'].append(explanation)
        
        print(f"   ✅ Exported {len(explanations_results)} category explanations")
        
        # Generate statistics
        print("📊 Generating statistics...")
        export_data['statistics'] = {
            "total_hierarchical_paths": len(export_data['categories']['hierarchical']),
            "categories_by_level": {
                f"level{i}": len(export_data['categories']['by_level'][f'level{i}']) 
                for i in range(1, 8)
            },
            "total_hard_logic_rules": len(export_data['logic_rules']['hard_logic']),
            "total_soft_logic_rules": len(export_data['logic_rules']['soft_logic']),
            "total_explanations": len(export_data['explanations']),
            "pattern_rules": len([rule for rule in export_data['logic_rules']['hard_logic'] if rule['is_pattern']]),
            "word_rules": len([rule for rule in export_data['logic_rules']['hard_logic'] if not rule['is_pattern']])
        }
        
        # Close database connection
        cursor.close()
        conn.close()
        
        return export_data
        
    except Exception as e:
        print(f"❌ Error exporting categories: {e}")
        return None

def main():
    print("🚀 Exporting All Categories from Database")
    print("=" * 50)
    
    # Export all data
    export_data = export_all_categories()
    
    if export_data:
        # Save to JSON file
        output_file = "categories_export.json"
        print(f"💾 Saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Export completed successfully!")
        print(f"\n📋 Export Summary:")
        print(f"   📁 File: {output_file}")
        print(f"   📊 Statistics:")
        for key, value in export_data['statistics'].items():
            if isinstance(value, dict):
                print(f"      {key}:")
                for sub_key, sub_value in value.items():
                    print(f"        {sub_key}: {sub_value}")
            else:
                print(f"      {key}: {value}")
        
        return True
    else:
        print("💥 Export failed!")
        return False

if __name__ == "__main__":
    main()

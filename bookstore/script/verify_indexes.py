"""
验证 MongoDB 索引是否已正确创建
"""
from pymongo import MongoClient
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "bookstore"

def verify_indexes():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    print("=" * 60)
    print("MongoDB 索引验证报告")
    print("=" * 60)
    
    # 1. books 集合索引
    print("\n1. books 集合索引:")
    try:
        books_indexes = db.books.index_information()
        # 检查 id 索引（可能是 "id_1" 或 "id"）
        id_index_found = any('id' in idx_name and idx_name != '_id_' for idx_name in books_indexes.keys())
        if id_index_found:
            print("   ✅ id 唯一索引存在")
        else:
            print("   ❌ id 索引缺失")
        
        # 检查 title 索引
        title_index_found = any('title' in idx_name and 'text' not in idx_name.lower() 
                               for idx_name in books_indexes.keys())
        if title_index_found:
            print("   ✅ title 索引存在")
        else:
            print("   ❌ title 索引缺失")
        
        # 检查 author 索引
        author_index_found = any('author' in idx_name and 'text' not in idx_name.lower() 
                                for idx_name in books_indexes.keys())
        if author_index_found:
            print("   ✅ author 索引存在")
        else:
            print("   ❌ author 索引缺失")
        
        # 检查全文索引
        text_index_found = any('text' in idx_name.lower() for idx_name in books_indexes.keys())
        if text_index_found:
            print("   ✅ 全文索引存在")
        else:
            print("   ⚠️  全文索引不存在（可能MongoDB版本不支持）")
        
        # 显示所有索引（调试用）
        print(f"   📋 实际索引: {list(books_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  books 集合不存在或无法访问: {e}")
    
    # 2. store_books 集合索引
    print("\n2. store_books 集合索引:")
    try:
        store_books_indexes = db.store_books.index_information()
        # 检查 title 索引
        title_index_found = any('title' in idx_name and 'text' not in idx_name.lower() 
                               for idx_name in store_books_indexes.keys())
        if title_index_found:
            print("   ✅ title 索引存在")
        else:
            print("   ❌ title 索引缺失")
        
        # 检查复合索引（MongoDB 会生成类似 "store_id_1_book_id_1" 的名称）
        compound_index_found = any('store_id' in idx_name and 'book_id' in idx_name 
                                  for idx_name in store_books_indexes.keys())
        if compound_index_found:
            print("   ✅ (store_id, book_id) 复合索引存在")
        else:
            print("   ❌ (store_id, book_id) 复合索引缺失")
        
        print(f"   📋 实际索引: {list(store_books_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  store_books 集合不存在或无法访问: {e}")
    
    # 3. orders 集合索引
    print("\n3. orders 集合索引:")
    try:
        orders_indexes = db.orders.index_information()
        # 检查各个索引（MongoDB 会自动添加 "_1" 后缀）
        order_id_found = any('order_id' in idx_name for idx_name in orders_indexes.keys())
        buyer_id_found = any('buyer_id' in idx_name for idx_name in orders_indexes.keys())
        store_id_found = any('store_id' in idx_name for idx_name in orders_indexes.keys())
        status_found = any('status' in idx_name for idx_name in orders_indexes.keys())
        created_time_found = any('created_time' in idx_name for idx_name in orders_indexes.keys())
        
        if order_id_found:
            print("   ✅ order_id 索引存在")
        else:
            print("   ❌ order_id 索引缺失")
        
        if buyer_id_found:
            print("   ✅ buyer_id 索引存在")
        else:
            print("   ❌ buyer_id 索引缺失")
        
        if store_id_found:
            print("   ✅ store_id 索引存在")
        else:
            print("   ❌ store_id 索引缺失")
        
        if status_found:
            print("   ✅ status 索引存在")
        else:
            print("   ❌ status 索引缺失")
        
        if created_time_found:
            print("   ✅ created_time 索引存在")
        else:
            print("   ❌ created_time 索引缺失")
        
        print(f"   📋 实际索引: {list(orders_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  orders 集合不存在或无法访问: {e}")
    
    # 4. order_items 集合索引
    print("\n4. order_items 集合索引:")
    try:
        order_items_indexes = db.order_items.index_information()
        order_id_found = any('order_id' in idx_name for idx_name in order_items_indexes.keys())
        if order_id_found:
            print("   ✅ order_id 索引存在")
        else:
            print("   ❌ order_id 索引缺失")
        print(f"   📋 实际索引: {list(order_items_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  order_items 集合不存在或无法访问: {e}")
    
    # 5. users 集合索引
    print("\n5. users 集合索引:")
    try:
        users_indexes = db.users.index_information()
        user_id_found = any('user_id' in idx_name for idx_name in users_indexes.keys())
        if user_id_found:
            print("   ✅ user_id 索引存在")
        else:
            print("   ❌ user_id 索引缺失")
        print(f"   📋 实际索引: {list(users_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  users 集合不存在或无法访问: {e}")
    
    # 6. stores 集合索引
    print("\n6. stores 集合索引:")
    try:
        stores_indexes = db.stores.index_information()
        store_id_found = any('store_id' in idx_name for idx_name in stores_indexes.keys())
        user_id_found = any('user_id' in idx_name for idx_name in stores_indexes.keys())
        
        if store_id_found:
            print("   ✅ store_id 索引存在")
        else:
            print("   ❌ store_id 索引缺失")
        
        if user_id_found:
            print("   ✅ user_id 索引存在")
        else:
            print("   ❌ user_id 索引缺失")
        
        print(f"   📋 实际索引: {list(stores_indexes.keys())}")
    except Exception as e:
        print(f"   ⚠️  stores 集合不存在或无法访问: {e}")
    
    print("\n" + "=" * 60)
    print("索引验证完成！")
    print("=" * 60)
    
    # 性能建议
    print("\n💡 性能优化建议:")
    print("1. 确保所有索引都已创建（运行 script/init_indexes.py）")
    print("2. 使用 explain() 分析查询计划，验证索引是否被使用")
    print("3. 定期监控慢查询，优化未使用索引的查询")
    print("4. 运行性能测试验证索引带来的性能提升")

if __name__ == "__main__":
    verify_indexes()


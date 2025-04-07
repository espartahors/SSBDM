from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Prefetch

from equipment_new.models import Area, Equipment
from spare_parts_new.models import SparePart, Category
from documents.models import EquipmentDocument
from .models import BOMRelationship


@login_required
def ssbom_browser(request):
    """Main view for the SSBOM browser interface."""
    return render(request, 'ssbom/ssbom_browser.html')


@login_required
def tree_data(request):
    """AJAX endpoint for getting tree structure data with filters."""
    hierarchy_type = request.GET.get('hierarchy_type', 'full')
    show_equipment = request.GET.get('show_equipment', 'true') == 'true'
    show_spare_parts = request.GET.get('show_spare_parts', 'true') == 'true'
    show_documents = request.GET.get('show_documents', 'true') == 'true'
    
    tree_data = []
    
    if hierarchy_type == 'full':
        # Full hierarchy starting with areas
        areas = Area.objects.all().order_by('name')
        
        for area in areas:
            area_node = {
                'id': f'area-{area.id}',
                'text': area.name,
                'type': 'area',
                'children': []
            }
            
            if show_equipment:
                equipments = Equipment.objects.filter(area=area).order_by('name')
                
                for equipment in equipments:
                    equipment_node = {
                        'id': f'equipment-{equipment.id}',
                        'text': equipment.name,
                        'type': 'equipment',
                        'children': []
                    }
                    
                    if show_spare_parts:
                        # First try to get spare parts from BOMRelationship
                        bom_spare_parts = BOMRelationship.objects.filter(
                            equipment=equipment, 
                            spare_part__isnull=False
                        ).select_related('spare_part', 'spare_part__category')
                        
                        # If no BOM relationships exist, fall back to the old method
                        if not bom_spare_parts.exists():
                            spare_parts = SparePart.objects.filter(equipment=equipment).distinct().order_by('name')
                            
                            for part in spare_parts:
                                part_node = {
                                    'id': f'spare-part-{part.id}',
                                    'text': part.name,
                                    'type': 'spare-part'
                                }
                                equipment_node['children'].append(part_node)
                        else:
                            # Use the BOM relationships
                            for rel in bom_spare_parts:
                                part = rel.spare_part
                                part_node = {
                                    'id': f'spare-part-{part.id}',
                                    'text': f"{part.name} ({rel.get_relationship_type_display()}: {rel.quantity})",
                                    'type': 'spare-part'
                                }
                                equipment_node['children'].append(part_node)
                    
                    if show_documents:
                        # First try to get documents from BOMRelationship
                        bom_documents = BOMRelationship.objects.filter(
                            equipment=equipment, 
                            document__isnull=False
                        ).select_related('document')
                        
                        # If no BOM relationships exist, fall back to the old method
                        if not bom_documents.exists():
                            documents = EquipmentDocument.objects.filter(equipment=equipment).order_by('title')
                            
                            for doc in documents:
                                doc_node = {
                                    'id': f'document-{doc.id}',
                                    'text': doc.title,
                                    'type': 'document'
                                }
                                equipment_node['children'].append(doc_node)
                        else:
                            # Use the BOM relationships
                            for rel in bom_documents:
                                doc = rel.document
                                doc_node = {
                                    'id': f'document-{doc.id}',
                                    'text': f"{doc.title} ({rel.get_relationship_type_display()})",
                                    'type': 'document'
                                }
                                equipment_node['children'].append(doc_node)
                    
                    if equipment_node['children'] or not (show_spare_parts or show_documents):
                        area_node['children'].append(equipment_node)
            
            if area_node['children'] or not show_equipment:
                tree_data.append(area_node)
                
    elif hierarchy_type == 'equipment':
        # Equipment only hierarchy
        areas = Area.objects.all().order_by('name')
        
        for area in areas:
            area_node = {
                'id': f'area-{area.id}',
                'text': area.name,
                'type': 'area',
                'children': []
            }
            
            equipments = Equipment.objects.filter(area=area).order_by('name')
            
            for equipment in equipments:
                equipment_node = {
                    'id': f'equipment-{equipment.id}',
                    'text': equipment.name,
                    'type': 'equipment'
                }
                area_node['children'].append(equipment_node)
            
            if area_node['children']:
                tree_data.append(area_node)
    
    elif hierarchy_type == 'spare-parts':
        # Spare parts by category hierarchy
        categories = Category.objects.all().order_by('name')
        
        for category in categories:
            category_node = {
                'id': f'category-{category.id}',
                'text': category.name,
                'type': 'category',
                'children': []
            }
            
            spare_parts = SparePart.objects.filter(category=category).order_by('name')
            
            for part in spare_parts:
                part_node = {
                    'id': f'spare-part-{part.id}',
                    'text': part.name,
                    'type': 'spare-part'
                }
                category_node['children'].append(part_node)
            
            if category_node['children']:
                tree_data.append(category_node)
    
    elif hierarchy_type == 'documents':
        # Documents by type hierarchy
        document_types = EquipmentDocument.objects.values('document_type').annotate(count=Count('id'))
        
        for doc_type in document_types:
            type_name = dict(EquipmentDocument.DOCUMENT_TYPES)[doc_type['document_type']]
            type_node = {
                'id': f'doc-type-{doc_type["document_type"]}',
                'text': type_name,
                'type': 'folder',
                'children': []
            }
            
            documents = EquipmentDocument.objects.filter(document_type=doc_type['document_type']).order_by('title')
            
            for doc in documents:
                doc_node = {
                    'id': f'document-{doc.id}',
                    'text': doc.title,
                    'type': 'document'
                }
                type_node['children'].append(doc_node)
            
            tree_data.append(type_node)
    
    return JsonResponse(tree_data, safe=False)


@login_required
def area_detail_ajax(request, pk):
    """AJAX endpoint for getting area details."""
    area = get_object_or_404(Area, pk=pk)
    equipment_list = Equipment.objects.filter(area=area).order_by('name')
    # Get documents related to equipment in this area
    equipments = Equipment.objects.filter(area=area)
    document_list = EquipmentDocument.objects.filter(equipment__in=equipments).order_by('title')
    
    context = {
        'area': area,
        'equipment_list': equipment_list,
        'document_list': document_list
    }
    
    return render(request, 'ssbom/partials/area_detail.html', context)


@login_required
def equipment_detail_ajax(request, pk):
    """AJAX endpoint for getting equipment details."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # Try to get spare parts from BOM relationships first
    bom_spare_parts = BOMRelationship.objects.filter(
        equipment=equipment,
        spare_part__isnull=False
    ).select_related('spare_part')
    
    # If no BOM relationships, fall back to direct relationships
    if bom_spare_parts.exists():
        spare_parts = [rel.spare_part for rel in bom_spare_parts]
        bom_relationships = bom_spare_parts
    else:
        spare_parts = SparePart.objects.filter(equipment=equipment).distinct().order_by('name')
        bom_relationships = None
    
    # Try to get documents from BOM relationships first
    bom_documents = BOMRelationship.objects.filter(
        equipment=equipment,
        document__isnull=False
    ).select_related('document')
    
    # If no BOM relationships, fall back to direct relationships
    if bom_documents.exists():
        documents = [rel.document for rel in bom_documents]
        document_relationships = bom_documents
    else:
        documents = EquipmentDocument.objects.filter(equipment=equipment).order_by('title')
        document_relationships = None
    
    context = {
        'equipment': equipment,
        'spare_parts': spare_parts,
        'documents': documents,
        'bom_relationships': bom_relationships,
        'document_relationships': document_relationships
    }
    
    return render(request, 'ssbom/partials/equipment_detail.html', context)


@login_required
def spare_part_detail_ajax(request, pk):
    """AJAX endpoint for getting spare part details."""
    spare_part = get_object_or_404(SparePart, pk=pk)
    
    # Try to get equipment from BOM relationships first
    bom_relationships = BOMRelationship.objects.filter(
        spare_part=spare_part
    ).select_related('equipment', 'equipment__area')
    
    # If no BOM relationships, fall back to direct relationships
    if bom_relationships.exists():
        equipment_list = [rel.equipment for rel in bom_relationships]
    else:
        equipment_list = Equipment.objects.filter(sparepart=spare_part).distinct().order_by('name')
    
    # Get documents related to equipment that uses this spare part
    equipments = Equipment.objects.filter(sparepart=spare_part)
    documents = EquipmentDocument.objects.filter(equipment__in=equipments).order_by('title')
    
    context = {
        'spare_part': spare_part,
        'equipment_list': equipment_list,
        'documents': documents,
        'bom_relationships': bom_relationships if bom_relationships.exists() else None
    }
    
    return render(request, 'ssbom/partials/spare_part_detail.html', context)


@login_required
def document_detail_ajax(request, pk):
    """AJAX endpoint for getting document details."""
    document = get_object_or_404(EquipmentDocument, pk=pk)
    
    # Try to get equipment from BOM relationships first
    bom_relationships = BOMRelationship.objects.filter(
        document=document
    ).select_related('equipment', 'equipment__area')
    
    # If no BOM relationships, fall back to direct relationships
    if bom_relationships.exists():
        equipment_list = [rel.equipment for rel in bom_relationships]
    else:
        equipment_list = [document.equipment]
    
    # Get spare parts related to this equipment
    spare_parts = SparePart.objects.filter(equipment__in=equipment_list).distinct().order_by('name')
    
    context = {
        'document': document,
        'equipment_list': equipment_list,
        'spare_parts': spare_parts,
        'bom_relationships': bom_relationships if bom_relationships.exists() else None
    }
    
    return render(request, 'ssbom/partials/document_detail.html', context)


@login_required
def category_detail_ajax(request, pk):
    """AJAX endpoint for getting category details."""
    category = get_object_or_404(Category, pk=pk)
    spare_parts = SparePart.objects.filter(category=category).order_by('name')
    
    # Calculate stats
    low_stock_count = spare_parts.filter(current_stock__lte=F('minimum_stock'), current_stock__gt=0).count()
    out_of_stock_count = spare_parts.filter(current_stock=0).count()
    
    context = {
        'category': category,
        'spare_parts': spare_parts,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count
    }
    
    return render(request, 'ssbom/partials/category_detail.html', context)


@login_required
def manage_relationships(request):
    """View for managing BOM relationships."""
    areas = Area.objects.all().prefetch_related('equipment_set').order_by('name')
    categories = Category.objects.all().prefetch_related('sparepart_set').order_by('name')
    documents = EquipmentDocument.objects.all().order_by('title')
    document_types = EquipmentDocument.DOCUMENT_TYPES
    
    context = {
        'areas': areas,
        'categories': categories,
        'documents': documents,
        'document_types': document_types,
    }
    
    return render(request, 'ssbom/manage_relationships.html', context)


@login_required
def get_equipment_relationships(request):
    """AJAX endpoint for getting relationships for an equipment."""
    equipment_id = request.GET.get('equipment_id')
    if not equipment_id:
        return JsonResponse({'error': 'No equipment ID provided'}, status=400)
    
    try:
        equipment = Equipment.objects.get(pk=equipment_id)
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipment not found'}, status=404)
    
    relationships = BOMRelationship.objects.filter(equipment=equipment).select_related('spare_part', 'document')
    
    relationship_data = []
    for rel in relationships:
        rel_data = {
            'id': rel.id,
            'relationship_type': rel.relationship_type,
            'relationship_type_display': rel.get_relationship_type_display(),
            'quantity': rel.quantity,
            'notes': rel.notes,
        }
        
        if rel.spare_part:
            rel_data['spare_part'] = True
            rel_data['spare_part_id'] = rel.spare_part.id
            rel_data['spare_part_name'] = rel.spare_part.name
            rel_data['spare_part_code'] = rel.spare_part.code
        
        if rel.document:
            rel_data['document'] = True
            rel_data['document_id'] = rel.document.id
            rel_data['document_title'] = rel.document.title
            rel_data['document_type'] = rel.document.document_type
        
        relationship_data.append(rel_data)
    
    return JsonResponse({
        'equipment': {
            'id': equipment.id,
            'name': equipment.name,
        },
        'relationships': relationship_data
    })


@login_required
def save_relationship(request):
    """AJAX endpoint for saving a BOM relationship."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    equipment_id = request.POST.get('equipment_id')
    relationship_type = request.POST.get('relationship_type')
    quantity = request.POST.get('quantity', 1)
    notes = request.POST.get('notes', '')
    
    spare_part_id = request.POST.get('spare_part_id')
    document_id = request.POST.get('document_id')
    
    # Validate inputs
    if not equipment_id:
        return JsonResponse({'error': 'Equipment ID is required'}, status=400)
    
    if not relationship_type:
        return JsonResponse({'error': 'Relationship type is required'}, status=400)
    
    if not spare_part_id and not document_id:
        return JsonResponse({'error': 'Either spare part or document ID is required'}, status=400)
    
    # Get objects
    try:
        equipment = Equipment.objects.get(pk=equipment_id)
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipment not found'}, status=404)
    
    spare_part = None
    document = None
    
    if spare_part_id:
        try:
            spare_part = SparePart.objects.get(pk=spare_part_id)
        except SparePart.DoesNotExist:
            return JsonResponse({'error': 'Spare part not found'}, status=404)
    
    if document_id:
        try:
            document = EquipmentDocument.objects.get(pk=document_id)
        except EquipmentDocument.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)
    
    # Create or update relationship
    try:
        if spare_part:
            # Check if relationship already exists
            rel, created = BOMRelationship.objects.get_or_create(
                equipment=equipment,
                spare_part=spare_part,
                relationship_type=relationship_type,
                defaults={
                    'quantity': quantity,
                    'notes': notes
                }
            )
            
            if not created:
                # Update existing relationship
                rel.quantity = quantity
                rel.notes = notes
                rel.save()
        
        elif document:
            # Check if relationship already exists
            rel, created = BOMRelationship.objects.get_or_create(
                equipment=equipment,
                document=document,
                relationship_type=relationship_type,
                defaults={
                    'quantity': quantity,
                    'notes': notes
                }
            )
            
            if not created:
                # Update existing relationship
                rel.quantity = quantity
                rel.notes = notes
                rel.save()
        
        return JsonResponse({'success': True, 'relationship_id': rel.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_relationship(request):
    """AJAX endpoint for deleting a BOM relationship."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    relationship_id = request.POST.get('relationship_id')
    
    if not relationship_id:
        return JsonResponse({'error': 'Relationship ID is required'}, status=400)
    
    try:
        relationship = BOMRelationship.objects.get(pk=relationship_id)
        relationship.delete()
        return JsonResponse({'success': True})
    except BOMRelationship.DoesNotExist:
        return JsonResponse({'error': 'Relationship not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 
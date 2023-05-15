function(doc)
{
    if (doc.doc_type == "User")
    {
        if(doc.activation_key != null)
        {
            emit(doc.date_joined, null);
        }
    }
}

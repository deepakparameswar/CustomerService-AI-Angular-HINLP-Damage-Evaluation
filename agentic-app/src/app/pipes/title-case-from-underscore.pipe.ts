import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'titleCaseFromUnderscore',
  standalone: true
})
export class TitleCaseFromUnderscorePipe implements PipeTransform {

  transform(value: string): string {
    if (!value) return '';

    return value
      .split('_')                                 // split by underscores
      .map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      )                                           // capitalize each word
      .join(' ');                                 // join with spaces
  }

}